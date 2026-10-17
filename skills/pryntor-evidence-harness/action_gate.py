#!/usr/bin/env python3
"""Pryntor R0 offline action preflight. This is NOT an authorization service."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

SCHEMA = 'pryntor-action-v1'
SAFE_VERBS = frozenset({'read', 'test', 'draft'})
KNOWN_VERBS = SAFE_VERBS | {'index', 'write', 'execute', 'send', 'deploy', 'purchase', 'delete'}
SENSITIVE_KEYS = re.compile(r'(?i)(password|secret|api.?key|access.?token|authorization|cookie|private.?key)')
SHA = re.compile(r'^[0-9a-f]{64}$')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def safe_digest(value):
    try:
        return digest(value)
    except (TypeError, ValueError):
        return None


def _date(value):
    if not isinstance(value, str):
        return None
    try:
        d = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None
    return d.astimezone(timezone.utc) if d.tzinfo else None


def _valid_policy(policy):
    if not isinstance(policy, dict) or policy.get('schema') != SCHEMA or policy.get('mode') != 'offline_r0':
        return False
    if set(policy) != {'schema', 'mode', 'allow_agents', 'allow_ventures', 'allow_tools', 'allow_resources', 'allow_data_classes'}:
        return False
    for key in ('allow_agents', 'allow_ventures', 'allow_tools', 'allow_resources', 'allow_data_classes'):
        values = policy.get(key)
        if not isinstance(values, list) or not values or any(not isinstance(x, str) or not x or x == '*' for x in values):
            return False
        if len(values) != len(set(values)):
            return False
    return set(policy['allow_data_classes']).issubset({'public', 'synthetic', 'internal'})


def evaluate(action, policy, now=None):
    """Advisory check only. No tool execution, approvals, or credential verification."""
    now = now or datetime.now(timezone.utc)
    reasons = []
    if not _valid_policy(policy):
        return {'schema': SCHEMA, 'decision': 'deny', 'reasons': ['invalid_policy'], 'release_authorized': False, 'tool_executed': False}
    if not isinstance(action, dict) or set(action) != {'schema', 'action_id', 'agent', 'venture', 'tool', 'resource', 'verb', 'data_class', 'estimated_cost_usd', 'instruction_source', 'evidence'}:
        reasons.append('invalid_action_shape')
        action = {}  # never echo raw inputs or potential secrets
    if action.get('schema') != SCHEMA:
        reasons.append('invalid_schema')
    for key, allowed_key in (('agent', 'allow_agents'), ('venture', 'allow_ventures'), ('tool', 'allow_tools'), ('resource', 'allow_resources'), ('data_class', 'allow_data_classes')):
        if not isinstance(action.get(key), str) or action.get(key) not in policy[allowed_key]:
            reasons.append('scope_denied:' + key)
    if not isinstance(action.get('action_id'), str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,95}', action['action_id']):
        reasons.append('invalid_action_id')
    verb = action.get('verb')
    if not isinstance(verb, str) or verb not in KNOWN_VERBS:
        reasons.append('unknown_verb')
    elif verb not in SAFE_VERBS:
        reasons.append('requires_separate_authority:' + verb)
    cost = action.get('estimated_cost_usd')
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost != 0:
        reasons.append('zero_spend_gate')
    if action.get('instruction_source') != 'reviewed_local_contract':
        reasons.append('untrusted_instruction_source')
    evidence = action.get('evidence')
    if not isinstance(evidence, dict) or set(evidence) != {'artifact_sha256', 'captured_at', 'source_type'}:
        reasons.append('missing_evidence_metadata')
    else:
        if not isinstance(evidence.get('artifact_sha256'), str) or not SHA.fullmatch(evidence['artifact_sha256']):
            reasons.append('invalid_digest')
        if evidence.get('source_type') != 'local_synthetic':
            reasons.append('unverified_source_type')
        captured = _date(evidence.get('captured_at'))
        if captured is None or captured > now + timedelta(seconds=30) or now - captured > timedelta(minutes=60):
            reasons.append('stale_or_invalid_timestamp')
    if any(SENSITIVE_KEYS.search(str(k)) for k in action):
        reasons.append('sensitive_field')
    decision = 'eligible_for_separate_read_only_authorization' if not reasons else 'deny'
    return {'schema': SCHEMA, 'decision': decision, 'reasons': sorted(set(reasons)),
            'release_authorized': False, 'tool_executed': False,
            'action_digest': safe_digest(action) if action else None,
            'policy_digest': digest(policy)}


def _event_hash(record):
    return digest({key: value for key, value in record.items() if key != 'event_hash'})


def verify_log(path):
    """Detects local edits/truncation within a supplied chain, NOT wholesale replacement."""
    previous = '0' * 64
    count = 0
    if not path.exists():
        return {'valid': True, 'events': 0, 'head': previous}
    try:
        for line in path.read_text(encoding='utf-8').splitlines():
            event = json.loads(line)
            if (not isinstance(event, dict) or set(event) != {'seq', 'previous_hash', 'decision_digest', 'event_hash'}
                    or type(event['seq']) is not int or event['seq'] != count + 1
                    or event['previous_hash'] != previous or not isinstance(event['decision_digest'], str)
                    or not SHA.fullmatch(event['decision_digest']) or event['event_hash'] != _event_hash(event)):
                return {'valid': False, 'events': count, 'reason': 'tampered_or_broken_chain'}
            previous = event['event_hash']
            count += 1
    except (OSError, ValueError, TypeError, KeyError):
        return {'valid': False, 'events': count, 'reason': 'invalid_log'}
    return {'valid': True, 'events': count, 'head': previous}


def append_log(path, verdict):
    """Local-only prototype. Caller must provide an isolated single-writer destination."""
    status = verify_log(path)
    if not status['valid']:
        raise ValueError('Refusing to append to invalid audit chain')
    if path.is_symlink():
        raise ValueError('Audit log symlink refused')
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {'seq': status['events'] + 1, 'previous_hash': status['head'], 'decision_digest': digest(verdict)}
    event['event_hash'] = _event_hash(event)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'a', encoding='utf-8') as output:
        output.write(canonical(event) + '\n')
        output.flush()
        os.fsync(output.fileno())
    return event['event_hash']


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline policy preflight, no tool invocation')
    commands = parser.add_subparsers(dest='command', required=True)
    check = commands.add_parser('check')
    check.add_argument('--action', type=Path, required=True)
    check.add_argument('--policy', type=Path, required=True)
    check.add_argument('--log', type=Path)
    verify = commands.add_parser('verify-log')
    verify.add_argument('--log', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'verify-log':
        status = verify_log(args.log)
        print(canonical(status))
        return 0 if status['valid'] else 2
    try:
        action = json.loads(args.action.read_text(encoding='utf-8'))
        policy = json.loads(args.policy.read_text(encoding='utf-8'))
        verdict = evaluate(action, policy)
        if args.log:
            append_log(args.log, verdict)
    except (OSError, ValueError, TypeError):
        print(canonical({'decision': 'deny', 'reason': 'invalid_input_or_audit', 'release_authorized': False}))
        return 2
    print(canonical(verdict))
    return 0 if verdict['decision'].startswith('eligible_') else 2


if __name__ == '__main__':
    sys.exit(main())
