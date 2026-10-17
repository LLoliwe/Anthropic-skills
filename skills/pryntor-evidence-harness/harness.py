#!/usr/bin/env python3
"""Pryntor evidence-gated local check runner. Standard library only, no AI/API calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

EXCLUDE_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'node_modules', 'graphify-out'}
MAX_OUTPUT = 16000


def snapshot(root: Path) -> str:
    """Content digest of regular project files, stable across traversal order."""
    root = root.resolve(strict=True)
    digest = hashlib.sha256()
    count = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS and not (Path(base) / d).is_symlink())
        for name in sorted(files):
            path = Path(base) / name
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"Disallowed non-regular project file: {path}")
            relative = path.relative_to(root).as_posix()
            digest.update(relative.encode('utf-8') + b'\0')
            with path.open('rb') as source:
                while data := source.read(65536):
                    digest.update(data)
            digest.update(b'\0')
            count += 1
    if count == 0:
        raise ValueError('Empty project: refuse verification')
    return digest.hexdigest()


def load_contract(path: Path) -> dict:
    contract = json.loads(path.read_text(encoding='utf-8'))
    if contract.get('schema') != 'pryntor-evidence-v1':
        raise ValueError('Unsupported contract schema')
    checks = contract.get('checks')
    requirements = contract.get('requirements')
    if not isinstance(checks, dict) or not checks or not isinstance(requirements, dict) or not requirements:
        raise ValueError('Must define nonempty checks and requirements')
    for check_id, check in checks.items():
        cmd = check.get('command') if isinstance(check, dict) else None
        timeout = check.get('timeout_seconds', 30) if isinstance(check, dict) else None
        if not check_id or not isinstance(cmd, list) or not cmd or not all(isinstance(s, str) and s for s in cmd):
            raise ValueError(f'Invalid command for {check_id}')
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < timeout <= 120:
            raise ValueError(f'Invalid bounded timeout for {check_id}')
    for requirement, required in requirements.items():
        if not requirement or not isinstance(required, list) or not required or any(c not in checks for c in required):
            raise ValueError(f'Unknown or missing check for {requirement}')
        if len(set(required)) != len(required):
            raise ValueError(f'Duplicate mandatory check for {requirement}')
    return contract


def execute(project: Path, contract: dict, claim: str = '') -> dict:
    project = project.resolve(strict=True)
    initial = snapshot(project)
    records = {}
    for check_id, spec in contract['checks'].items():
        before = snapshot(project)
        started = datetime.now(timezone.utc).isoformat()
        start = time.monotonic()
        try:
            result = subprocess.run(spec['command'], shell=False, cwd=project, capture_output=True,
                                    text=True, errors='replace', timeout=spec.get('timeout_seconds', 30),
                                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            code, stdout, stderr = result.returncode, result.stdout[-MAX_OUTPUT:], result.stderr[-MAX_OUTPUT:]
            state = 'executed'
        except (subprocess.TimeoutExpired, OSError) as error:
            code, stdout, stderr, state = None, '', str(error)[-MAX_OUTPUT:], 'runner_error'
        after = snapshot(project)
        records[check_id] = {'check_id': check_id, 'command': spec['command'], 'started_at': started,
                             'elapsed_seconds': round(time.monotonic() - start, 4), 'snapshot_before': before,
                             'snapshot_after': after, 'exit_code': code, 'runner_state': state,
                             'stdout_tail': stdout, 'stderr_tail': stderr}
    return {'schema': 'pryntor-evidence-v1', 'project_snapshot_before': initial,
            'project_snapshot_after': snapshot(project), 'worker_claim_untrusted': claim, 'checks': records}


def evaluate(contract: dict, record: dict, current_snapshot: str) -> dict:
    """No judge/worker value can promote a missing, stale, failed or mutating check."""
    results = {}
    records = record.get('checks', {})
    for requirement, ids in contract['requirements'].items():
        findings = []
        for check_id in ids:
            check = records.get(check_id)
            if check is None or check.get('runner_state') != 'executed':
                findings.append({'check': check_id, 'status': 'unverified', 'reason': 'missing_or_runner_error'})
            elif (check.get('snapshot_before') != current_snapshot or
                  check.get('snapshot_after') != current_snapshot):
                findings.append({'check': check_id, 'status': 'unverified', 'reason': 'stale_or_mutating'})
            elif check.get('command') != contract['checks'][check_id]['command']:
                findings.append({'check': check_id, 'status': 'unverified', 'reason': 'contract_mismatch'})
            elif check.get('exit_code') == 0:
                findings.append({'check': check_id, 'status': 'passed', 'reason': 'current_zero_exit'})
            elif check.get('exit_code') == 1:
                findings.append({'check': check_id, 'status': 'failed', 'reason': 'current_assertion_failure'})
            else:
                findings.append({'check': check_id, 'status': 'unverified', 'reason': 'unexpected_exit'})
        status = ('failed' if any(x['status'] == 'failed' for x in findings) else
                  'passed' if all(x['status'] == 'passed' for x in findings) else 'unverified')
        results[requirement] = {'status': status, 'evidence': findings}
    complete = all(r['status'] == 'passed' for r in results.values())
    return {'decision': 'contract_satisfied' if complete else 'hold', 'scope': 'contract_only',
            'current_snapshot': current_snapshot, 'requirements': results,
            'release_authorized': False, 'reason': 'Independent review and release approval always separate'}


def route_diagnostic(response: dict | None, allowed: set[str], minimum_confidence: float = 0.60) -> dict:
    """Optional typed judge can propose only an allowlisted ID. It never executes commands."""
    if not isinstance(response, dict) or response.get('type') != 'choice':
        return {'action': 'stop_for_review', 'reason': 'judge_missing_or_invalid'}
    choice, conf, probs = response.get('choice'), response.get('confidence'), response.get('probabilities')
    if not isinstance(probs, dict) or not isinstance(conf, (int, float)) or isinstance(conf, bool):
        return {'action': 'stop_for_review', 'reason': 'judge_invalid_distribution'}
    if not 0 <= conf <= 1 or not all(isinstance(p, (int, float)) and not isinstance(p, bool) and 0 <= p <= 1 for p in probs.values()) or abs(sum(probs.values()) - 1) > 0.03:
        return {'action': 'stop_for_review', 'reason': 'judge_invalid_distribution'}
    if choice not in allowed and choice != 'none_suitable':
        return {'action': 'stop_for_review', 'reason': 'unregistered_diagnostic'}
    if conf < minimum_confidence:
        return {'action': 'stop_for_review', 'reason': 'low_confidence'}
    if choice not in probs or probs[choice] < max(probs.values()):
        return {'action': 'stop_for_review', 'reason': 'inconsistent_choice'}
    return ({'action': 'stop_for_review', 'reason': 'no_suitable_diagnostic'} if choice == 'none_suitable' else
            {'action': 'suggest_registered_check', 'check_id': choice})


def main() -> int:
    parser = argparse.ArgumentParser(description='Local fail-closed evidence harness; no cloud spend')
    parser.add_argument('mode', choices=['run', 'replay'])
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--claim', default='')
    args = parser.parse_args()
    project = args.project.resolve(strict=True)
    contract = load_contract(args.contract)
    if args.mode == 'run':
        if args.evidence.resolve().is_relative_to(project):
            parser.error('Evidence output must be outside the project to preserve the source snapshot')
        evidence = execute(project, contract, args.claim)
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    else:
        evidence = json.loads(args.evidence.read_text(encoding='utf-8'))
    verdict = evaluate(contract, evidence, snapshot(project))
    print(json.dumps(verdict, indent=2))
    return 0 if verdict['decision'] == 'contract_satisfied' else 2


if __name__ == '__main__':
    sys.exit(main())