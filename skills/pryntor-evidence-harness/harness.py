#!/usr/bin/env python3
"""Pryntor Sentinel V2: offline, evidence-gated inspection and bounded verification.

Trusted contracts are executable code. This tool is not a sandbox, a signer, or a release approval.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
import uuid

RECORD_SCHEMA = 'pryntor-evidence-v2'
CONTRACT_SCHEMA = 'pryntor-evidence-v1'
POLICY_VERSION = 'sentinel-2.0'
EXCLUDE_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'node_modules', 'graphify-out'}
MAX_OUTPUT = 4000
MAX_SNAPSHOT_FILES = 100_000
MAX_SNAPSHOT_BYTES = 1_073_741_824
SECRET_PATTERNS = [
    re.compile(r'(?i)(bearer\s+)[A-Za-z0-9_\.\-/+=]{8,}'),
    re.compile(r'(?i)((?:api[_-]?key|authorization|token|password|secret)\s*[:=]\s*)\S+'),
    re.compile(r'\b(?:sk-(?:proj-)?|gh[pousr]_|github_pat_)[A-Za-z0-9_-]{12,}\b'),
]


def canonical_bytes(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(root: Path) -> str:
    """Digest in-scope regular files. Refuse symlinks, even symlinked directories."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Project must be a directory')
    digest = hashlib.sha256()
    count, total = 0, 0
    for base, dirs, files in os.walk(root, followlinks=False):
        # Symlinks to directories are never silently skipped. Excluded folders are
        # out of the content-integrity claim and must be protected separately.
        for name in dirs:
            if (Path(base) / name).is_symlink():
                raise ValueError(f'Symlink directory in project: {Path(base) / name}')
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
        for name in sorted(files):
            path = Path(base) / name
            if path.is_symlink() or not path.is_file():
                raise ValueError(f'Disallowed non-regular project file: {path}')
            if name in {'.DS_Store'}:
                continue
            relative = path.relative_to(root).as_posix()
            digest.update(relative.encode('utf-8') + b'\0')
            with path.open('rb') as source:
                while chunk := source.read(65536):
                    total += len(chunk)
                    if total > MAX_SNAPSHOT_BYTES:
                        raise ValueError('Project snapshot exceeds bounded size')
                    digest.update(chunk)
            digest.update(b'\0')
            count += 1
            if count > MAX_SNAPSHOT_FILES:
                raise ValueError('Project snapshot exceeds bounded file count')
    if not count:
        raise ValueError('Empty project: refuse verification')
    return digest.hexdigest()


def load_contract(path: Path) -> dict:
    contract = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(contract, dict) or contract.get('schema') != CONTRACT_SCHEMA:
        raise ValueError('Unsupported contract schema')
    checks, requirements = contract.get('checks'), contract.get('requirements')
    if not isinstance(checks, dict) or not checks or not isinstance(requirements, dict) or not requirements:
        raise ValueError('Must define nonempty checks and requirements')
    for check_id, check in checks.items():
        cmd = check.get('command') if isinstance(check, dict) else None
        timeout = check.get('timeout_seconds', 30) if isinstance(check, dict) else None
        if (not isinstance(check_id, str) or not check_id or not isinstance(cmd, list)
                or not cmd or not all(isinstance(s, str) and s and '\x00' not in s for s in cmd)):
            raise ValueError(f'Invalid command for {check_id}')
        if (not isinstance(timeout, (int, float)) or isinstance(timeout, bool)
                or not math.isfinite(timeout) or not 0 < timeout <= 120):
            raise ValueError(f'Invalid bounded timeout for {check_id}')
    for requirement, required in requirements.items():
        if (not isinstance(requirement, str) or not requirement or not isinstance(required, list)
                or not required or any(not isinstance(c, str) or c not in checks for c in required)):
            raise ValueError(f'Unknown or missing check for {requirement}')
        if len(set(required)) != len(required):
            raise ValueError(f'Duplicate mandatory check for {requirement}')
    return contract


def contract_digest(contract: dict) -> str:
    return sha256(canonical_bytes(contract))


def _tail(stream, limit: int = MAX_OUTPUT) -> tuple[str, int, str]:
    """Obtain bounded output, count and digest without loading the entire stream."""
    stream.flush()
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    h = hashlib.sha256()
    while b := stream.read(65536):
        h.update(b)
    stream.seek(max(0, size - limit))
    tail = stream.read(limit).decode('utf-8', errors='replace')
    return h.hexdigest(), size, tail


def _redact(value: str) -> str:
    for pat in SECRET_PATTERNS:
        if pat.groups:
            value = pat.sub(lambda m: m.group(1) + '[REDACTED]', value)
        else:
            value = pat.sub('[REDACTED]', value)
    return value


def _kill_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except OSError:
        process.kill()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def _execute_check(project: Path, command: list[str], timeout: float, include_output: bool) -> dict:
    # stdout and stderr stream to temporary files; malicious/massive output never
    # expands Python process memory. This does not limit disk writes by checks.
    subprocess_env = {key: os.environ[key] for key in ('PATH', 'LANG', 'LC_ALL', 'SYSTEMROOT') if key in os.environ}
    subprocess_env.update({'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1', 'HOME': '/nonexistent'})
    with tempfile.TemporaryFile(mode='w+b') as out, tempfile.TemporaryFile(mode='w+b') as err:
        try:
            p = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL,
                                 stdout=out, stderr=err, env=subprocess_env,
                                 start_new_session=True, close_fds=True)
        except OSError as error:
            return {'exit_code': None, 'runner_state': 'runner_error',
                    'runner_error': f'process_start_error:{type(error).__name__}',
                    'stdout_sha256': sha256(b''), 'stderr_sha256': sha256(b''),
                    'stdout_bytes': 0, 'stderr_bytes': 0,
                    'stdout_tail': '', 'stderr_tail': ''}
        try:
            code = p.wait(timeout=timeout)
            state = 'executed'
        except subprocess.TimeoutExpired:
            code, state = None, 'timeout'
        finally:
            # Even on a normal parent exit, terminate any same-session descendants.
            # This is bounded cleanup, not OS-level sandboxing.
            _kill_group(p)
        oh, ob, ot = _tail(out)
        eh, eb, et = _tail(err)
        return {'exit_code': code, 'runner_state': state,
                'stdout_sha256': oh, 'stderr_sha256': eh,
                'stdout_bytes': ob, 'stderr_bytes': eb,
                'stdout_tail': _redact(ot) if include_output else '',
                'stderr_tail': _redact(et) if include_output else ''}


def record_digest(record: dict) -> str:
    return sha256(canonical_bytes({k: v for k, v in record.items() if k != 'record_digest'}))


def execute(project: Path, contract: dict, claim: str = '', include_output: bool = False) -> dict:
    project = project.resolve(strict=True)
    initial = snapshot(project)
    records = {}
    for check_id, spec in contract['checks'].items():
        before = snapshot(project)
        started = datetime.now(timezone.utc).isoformat()
        begin = time.monotonic()
        result = _execute_check(project, spec['command'], spec.get('timeout_seconds', 30), include_output)
        after = snapshot(project)
        records[check_id] = {'check_id': check_id, 'command': spec['command'],
                             'started_at': started, 'elapsed_seconds': round(time.monotonic() - begin, 4),
                             'snapshot_before': before, 'snapshot_after': after, **result}
    result = {'schema': RECORD_SCHEMA, 'policy': POLICY_VERSION,
              'run_id': str(uuid.uuid4()), 'created_at': datetime.now(timezone.utc).isoformat(),
              'contract_digest': contract_digest(contract),
              'project_snapshot_before': initial, 'project_snapshot_after': snapshot(project),
              'scope_exclusions': sorted(EXCLUDE_DIRS),
              'worker_claim_untrusted': claim, 'checks': records}
    result['record_digest'] = record_digest(result)
    return result


def evaluate(contract: dict, record: dict, current_snapshot: str) -> dict:
    """Fail closed on missing, stale, forged-looking, failed or altered evidence."""
    held = lambda reason: {'decision': 'hold', 'scope': 'contract_only',
                           'current_snapshot': current_snapshot, 'requirements': {},
                           'release_authorized': False, 'reason': reason}
    if not isinstance(record, dict) or record.get('schema') != RECORD_SCHEMA or record.get('policy') != POLICY_VERSION:
        return held('record_schema_or_policy_mismatch')
    if record.get('contract_digest') != contract_digest(contract):
        return held('contract_mismatch')
    if record.get('record_digest') != record_digest(record):
        return held('record_corrupt_or_modified')
    if (record.get('project_snapshot_before') != current_snapshot
            or record.get('project_snapshot_after') != current_snapshot):
        return held('project_changed_during_or_after_run')
    records = record.get('checks')
    if not isinstance(records, dict) or set(records) != set(contract['checks']):
        return held('missing_or_extra_checks')
    results = {}
    for requirement, ids in contract['requirements'].items():
        findings = []
        for check_id in ids:
            check = records.get(check_id)
            if not isinstance(check, dict) or check.get('check_id') != check_id:
                findings.append({'check': check_id, 'status': 'unverified', 'reason': 'missing_or_invalid_check'})
            elif check.get('runner_state') != 'executed':
                findings.append({'check': check_id, 'status': 'unverified', 'reason': 'runner_error_or_timeout'})
            elif (check.get('snapshot_before') != current_snapshot or
                  check.get('snapshot_after') != current_snapshot):
                findings.append({'check': check_id, 'status': 'unverified', 'reason': 'stale_or_mutating'})
            elif check.get('command') != contract['checks'][check_id]['command']:
                findings.append({'check': check_id, 'status': 'unverified', 'reason': 'command_mismatch'})
            elif check.get('exit_code') == 0:
                findings.append({'check': check_id, 'status': 'passed', 'reason': 'current_zero_exit'})
            elif check.get('exit_code') == 1:
                findings.append({'check': check_id, 'status': 'failed', 'reason': 'current_assertion_failure'})
            else:
                findings.append({'check': check_id, 'status': 'unverified', 'reason': 'unexpected_exit'})
        status = ('failed' if any(f['status'] == 'failed' for f in findings) else
                  'passed' if all(f['status'] == 'passed' for f in findings) else 'unverified')
        results[requirement] = {'status': status, 'evidence': findings}
    complete = all(r['status'] == 'passed' for r in results.values())
    return {'decision': 'contract_satisfied' if complete else 'hold', 'scope': 'contract_only',
            'current_snapshot': current_snapshot, 'requirements': results,
            'release_authorized': False,
            'reason': 'Contract checks passed; review and release gates remain separate' if complete
                      else 'Unverified or failing mandatory criterion'}


def route_diagnostic(response: dict | None, allowed: set[str], minimum_confidence: float = .60,
                     minimum_choice_probability: float = .65) -> dict:
    """Advisory only: no model response becomes code or a release decision."""
    stop = lambda reason: {'action': 'stop_for_review', 'reason': reason}
    if not isinstance(response, dict) or response.get('type') != 'choice':
        return stop('judge_missing_or_invalid')
    choice, conf, probs = response.get('choice'), response.get('confidence'), response.get('probabilities')
    if (not isinstance(probs, dict) or not probs or not isinstance(conf, (int, float))
            or isinstance(conf, bool) or not math.isfinite(conf) or not 0 <= conf <= 1):
        return stop('judge_invalid_distribution')
    if choice not in allowed and choice != 'none_suitable':
        return stop('unregistered_diagnostic')
    if (not set(probs).issubset(allowed | {'none_suitable'})
            or any(not isinstance(p, (int, float)) or isinstance(p, bool) or not math.isfinite(p)
                   or not 0 <= p <= 1 for p in probs.values())
            or abs(sum(probs.values()) - 1) > .03):
        return stop('judge_invalid_distribution')
    if choice not in probs or probs[choice] < max(probs.values()):
        return stop('inconsistent_choice')
    if conf < minimum_confidence or probs[choice] < minimum_choice_probability:
        return stop('low_confidence_or_weak_winner')
    return stop('no_suitable_diagnostic') if choice == 'none_suitable' else {
        'action': 'suggest_registered_check', 'check_id': choice}


def render_html(record: dict, verdict: dict) -> str:
    """Pure static audit page; untrusted worker/output strings are escaped."""
    esc = lambda value: html.escape(str(value), quote=True)
    statuses = []
    for rid, info in verdict.get('requirements', {}).items():
        details = ', '.join(f"{item['check']}: {item['reason']}" for item in info['evidence'])
        statuses.append(f'<tr><td>{esc(rid)}</td><td>{esc(info["status"].upper())}</td><td>{esc(details)}</td></tr>')
    check_rows = []
    for check_id, check in record.get('checks', {}).items():
        check_rows.append('<tr><td>' + esc(check_id) + '</td><td>' + esc(check.get('runner_state')) +
                          '</td><td>' + esc(check.get('exit_code')) + '</td><td>' +
                          esc(check.get('elapsed_seconds')) + 's</td></tr>')
    status = 'CONTRACT SATISFIED, RELEASE HELD' if verdict['decision'] == 'contract_satisfied' else 'HOLD: UNVERIFIED'
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; object-src 'none'">
<title>Pryntor Sentinel | Offline Evidence</title><style>
:root{{color-scheme:dark}}body{{font-family:system-ui,-apple-system,sans-serif;background:#0b0d13;color:#eef2f8;max-width:1080px;margin:auto;padding:32px 22px}}
h1{{font-size:38px;letter-spacing:-1.5px;margin:8px 0}}small,dt{{color:#929eae}}header{{border-bottom:1px solid #354052;padding-bottom:22px}}
.status{{font-weight:800;color:#ffd384;padding:14px 0;font-size:21px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:20px 0}}
.card{{background:#171d28;border:1px solid #354052;border-radius:13px;padding:20px;overflow-wrap:anywhere}}.value{{font-family:ui-monospace,monospace;font-size:14px;overflow-wrap:anywhere}}
table{{border-collapse:collapse;width:100%;background:#171d28;margin-bottom:30px}}td,th{{border-bottom:1px solid #354052;padding:13px;text-align:left;vertical-align:top;overflow-wrap:anywhere}}
section{{margin-top:35px;overflow-x:auto}}h2{{font-size:21px}}.muted{{color:#a9b2c0}}.warning{{border:1px solid #ffd384;padding:15px;border-radius:12px;color:#ffd384}}
</style></head><body><header><small>PRYNTOR // SENTINEL V2 • OFFLINE VERIFICATION</small><h1>Evidence is not a claim.</h1>
<div class="status">{esc(status)}</div><div class="warning">RELEASE AUTHORIZED: NO. This page is a local test record, not independent security review or a product release.</div></header>
<div class="cards"><div class="card"><small>Decision</small><p>{esc(verdict['decision'])}</p></div><div class="card"><small>Run ID</small><p class="value">{esc(record.get('run_id', 'unknown'))}</p></div>
<div class="card"><small>Contract SHA-256</small><p class="value">{esc(record.get('contract_digest','missing'))}</p></div>
<div class="card"><small>Project SHA-256</small><p class="value">{esc(verdict.get('current_snapshot','missing'))}</p></div></div>
<section><h2>Mandatory requirements</h2><table><thead><tr><th>Criterion</th><th>Result</th><th>Evidence</th></tr></thead><tbody>{''.join(statuses)}</tbody></table></section>
<section><h2>Executed checks</h2><table><thead><tr><th>Check</th><th>Runner</th><th>Exit</th><th>Duration</th></tr></thead><tbody>{''.join(check_rows)}</tbody></table></section>
<section><h2>Worker assertion (never acceptance evidence)</h2><div class="card">{esc(record.get('worker_claim_untrusted',''))}</div></section>
<section><h2>Provenance and limits</h2><div class="card"><p>Policy: {esc(record.get('policy','unknown'))} • Record checksum: <span class="value">{esc(record.get('record_digest','missing'))}</span></p>
<p>Excluded directories: {esc(', '.join(record.get('scope_exclusions',[])))}</p><p class="muted">SHA-256 detects changes, not deliberate forgery. Trusted contract code must be reviewed. Not an execution sandbox. No external service is contacted by this report.</p></div></section>
</body></html>'''


def exclusive_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())


def main() -> int:
    parser = argparse.ArgumentParser(description='Pryntor Sentinel V2, offline evidence without external keys')
    parser.add_argument('mode', choices=['digest', 'run', 'replay', 'render'])
    parser.add_argument('--project', type=Path)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--html', type=Path, dest='html_path')
    parser.add_argument('--approved-contract-sha256', help='Explicit reviewed canonical contract digest required for run/replay')
    parser.add_argument('--claim', default='')
    parser.add_argument('--include-output', action='store_true', help='Sensitive: opt in to redacted log tails')
    args = parser.parse_args()
    try:
        contract = load_contract(args.contract)
        digest = contract_digest(contract)
        if args.mode == 'digest':
            print(digest)
            return 0
        if not args.project or not args.evidence:
            parser.error('--project and --evidence required for run/replay/render')
        project = args.project.resolve(strict=True)
        if args.evidence.resolve().is_relative_to(project) or (args.html_path and args.html_path.resolve().is_relative_to(project)):
            parser.error('Evidence and HTML output must be outside project snapshot scope')
        if args.mode in ('run', 'replay') and args.approved_contract_sha256 != digest:
            print('HOLD: contract digest not reviewed/pinned for this invocation', file=sys.stderr)
            return 2
        if args.mode == 'run':
            if args.evidence.exists() or args.evidence.is_symlink():
                parser.error('Evidence path already exists; use a unique, immutable output name')
            evidence = execute(project, contract, args.claim, args.include_output)
            exclusive_write(args.evidence, json.dumps(evidence, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
        else:
            evidence = json.loads(args.evidence.read_text(encoding='utf-8'))
        verdict = evaluate(contract, evidence, snapshot(project))
        if args.html_path:
            exclusive_write(args.html_path, render_html(evidence, verdict))
        print(json.dumps(verdict, indent=2))
        return 0 if verdict['decision'] == 'contract_satisfied' else 2
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f'HOLD: {type(error).__name__}: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())