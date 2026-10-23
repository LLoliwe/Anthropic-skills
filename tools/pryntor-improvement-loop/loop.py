#!/usr/bin/env python3
"""Offline, review-only improvement-loop controller. Not an OS sandbox."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

SKIP = {'.git', '.env', '.venv', 'node_modules', '__pycache__', '.pryntor-loop'}
MAX_ATTEMPTS = 5


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root):
    out = {}
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if any(part in SKIP or part.startswith('.env') for part in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError('Symlinks are not permitted in the staged workspace')
        if path.is_file():
            out[str(rel)] = path.read_bytes()
    return out


def run(argv, cwd, seconds, env):
    try:
        result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, timeout=seconds, check=False)
        return {'exit_code': result.returncode, 'stdout_sha256': digest(result.stdout),
                'stderr_sha256': digest(result.stderr), 'timeout': False}
    except subprocess.TimeoutExpired:
        return {'exit_code': None, 'stdout_sha256': None, 'stderr_sha256': None, 'timeout': True}
    except OSError as exc:
        return {'exit_code': None, 'error': type(exc).__name__, 'timeout': False}


def verify_in_copy(argv, work, seconds, env, protected):
    """Execute a verifier on a disposable copy so it cannot heal the candidate tree."""
    with tempfile.TemporaryDirectory(prefix='pryntor-verify-') as temp:
        stage = Path(temp) / 'workspace'
        shutil.copytree(work, stage)
        before = snapshot(stage)
        verify_env = {k: v for k, v in env.items() if k != 'PRYNTOR_LOOP_FEEDBACK_FILE'}
        result = run(argv, stage, seconds, verify_env)
        after = snapshot(stage)
        intact = all(after.get(p) == before.get(p) for p in protected)
        return result, intact


def ensure_argv(argv):
    if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or not x for x in argv):
        raise ValueError('Commands must be nonempty argument arrays, never shell strings')
    if any('\x00' in x for x in argv):
        raise ValueError('Invalid command argument')


def safe_path(path):
    p = Path(path)
    if p.is_absolute() or not p.parts or '..' in p.parts or any(part in SKIP for part in p.parts):
        raise ValueError('Unsafe or excluded relative path: ' + path)
    return p


def patch_for(before, after):
    result = []
    for name in sorted(set(before) | set(after)):
        if before.get(name) == after.get(name):
            continue
        a, b = before.get(name, b''), after.get(name, b'')
        try:
            old = a.decode('utf-8').splitlines()
            new = b.decode('utf-8').splitlines()
        except UnicodeDecodeError:
            raise ValueError('Binary changes cannot be exported automatically: ' + name)
        result.extend(line + '\n' for line in difflib.unified_diff(old, new, fromfile='a/' + name,
                                          tofile='b/' + name, lineterm=''))
    return ''.join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True, type=Path)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--execute', action='store_true', help='Explicit opt-in; default is no execution')
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding='utf-8'))
    allowed_keys = {'goal', 'candidate_argv', 'verify_argv', 'protected_files', 'max_attempts', 'timeout_seconds'}
    if set(spec) - allowed_keys or not isinstance(spec.get('goal'), str) or not spec['goal'].strip():
        raise ValueError('Spec has unknown fields or no goal')
    ensure_argv(spec.get('candidate_argv'))
    ensure_argv(spec.get('verify_argv'))
    count = spec.get('max_attempts', 3)
    timeout = spec.get('timeout_seconds', 20)
    if type(count) is not int or not 1 <= count <= MAX_ATTEMPTS:
        raise ValueError('max_attempts must be between 1 and 5')
    if type(timeout) is not int or not 1 <= timeout <= 60:
        raise ValueError('timeout_seconds must be between 1 and 60')
    files = spec.get('protected_files')
    if not isinstance(files, list) or not files or any(not isinstance(p, str) for p in files):
        raise ValueError('At least one protected verifier file is required')
    protected = [str(safe_path(p)) for p in files]
    root = args.root.resolve(strict=True)
    if not root.is_dir() or args.out.resolve() == root or root in args.out.resolve().parents:
        raise ValueError('Output must be outside source workspace')
    baseline_files = snapshot(root)
    if any(p not in baseline_files for p in protected):
        raise ValueError('Protected verifier is absent from staged workspace')
    if not args.execute:
        print(json.dumps({'status': 'DRY_RUN', 'goal': spec['goal'], 'max_attempts': count,
                          'protected_files': protected, 'paid_spend_authorized': False}))
        return 0
    args.out.mkdir(parents=True, exist_ok=False)
    events = args.out / 'events.jsonl'
    approved_env = {k: os.environ[k] for k in ('PATH', 'SYSTEMROOT', 'WINDIR', 'LANG') if k in os.environ}
    approved_env['PYTHONDONTWRITEBYTECODE'] = '1'
    status = 'NOT_STARTED'
    with tempfile.TemporaryDirectory(prefix='pryntor-loop-') as temp:
        work = Path(temp) / 'workspace'
        shutil.copytree(root, work, ignore=shutil.ignore_patterns('.git', '.env', '.env.*', '.venv',
                                                                  'node_modules', '__pycache__', '.pryntor-loop'))
        feedback = work / '.pryntor-loop'
        feedback.mkdir()
        approved_env['PRYNTOR_LOOP_FEEDBACK_FILE'] = str(feedback / 'feedback.json')
        initial = snapshot(work)
        baseline, baseline_integrity = verify_in_copy(spec['verify_argv'], work, timeout, approved_env, protected)
        with events.open('a', encoding='utf-8') as f:
            f.write(json.dumps({'event': 'baseline', 'verification': baseline}) + '\n')
        if not baseline_integrity:
            status = 'BLOCKED_BASELINE_VERIFIER_MODIFIED'
        elif baseline['exit_code'] is None:
            status = 'BLOCKED_BASELINE_UNAVAILABLE'
        elif baseline['exit_code'] == 0:
            status = 'ALREADY_PASSING'
        else:
            last_state = None
            for attempt in range(1, count + 1):
                started = time.monotonic()
                candidate = run(spec['candidate_argv'], work, timeout, approved_env)
                current = snapshot(work)
                integrity_ok = all(current.get(p) == initial.get(p) for p in protected)
                changed_source = current != initial
                verify, verify_integrity = (
                    verify_in_copy(spec['verify_argv'], work, timeout, approved_env, protected)
                    if integrity_ok and changed_source and candidate['exit_code'] == 0 else (None, True)
                )
                passed = bool(integrity_ok and changed_source and verify_integrity
                              and verify is not None and verify['exit_code'] == 0)
                state = digest(b''.join(k.encode() + digest(v).encode() for k, v in sorted(current.items())))
                event = {'event': 'attempt', 'n': attempt, 'candidate': candidate, 'verify': verify,
                         'protected_integrity': integrity_ok, 'verifier_integrity': verify_integrity,
                         'candidate_changed_source': changed_source, 'passed': passed,
                         'workspace_sha256': state, 'elapsed_seconds': round(time.monotonic() - started, 3)}
                with events.open('a', encoding='utf-8') as f:
                    f.write(json.dumps(event, sort_keys=True) + '\n')
                if not integrity_ok or not verify_integrity:
                    status = 'BLOCKED_VERIFIER_MODIFIED'
                    break
                if passed:
                    patch = patch_for(initial, current)
                    if not patch.strip():
                        status = 'BLOCKED_NO_EXPORTABLE_CHANGE'
                        break
                    (args.out / 'candidate.patch').write_text(patch, encoding='utf-8')
                    status = 'CANDIDATE_VERIFIED_REVIEW_REQUIRED'
                    break
                if state == last_state:
                    status = 'STOPPED_NO_PROGRESS'
                    break
                last_state = state
                (feedback / 'feedback.json').write_text(json.dumps(event), encoding='utf-8')
            else:
                status = 'STOPPED_ATTEMPT_LIMIT'
    receipt = {'status': status, 'goal': spec['goal'], 'baseline_verifier_sha256':
               {p: digest(baseline_files[p]) for p in protected}, 'paid_spend_authorized': False,
               'promotion': 'PROHIBITED_PENDING_HUMAN_REVIEW'}
    (args.out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt))
    return 0 if status in ('ALREADY_PASSING', 'CANDIDATE_VERIFIED_REVIEW_REQUIRED') else 2


if __name__ == '__main__':
    raise SystemExit(main())