#!/usr/bin/env python3
"""WTB&W R0: structural review-only preflight, NEVER real-world assurance."""
import argparse
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

H = re.compile(r"^[0-9a-fA-F]{64}$")
C = re.compile(r"^[0-9a-fA-F]{40}$")
GATES = ("rights", "privacy", "safety", "originality", "source_fidelity", "zero_new_spend")
METRICS = ("correctness", "experience", "originality", "reliability", "efficiency", "accessibility", "safety", "commercial")


def weburl(u):
    try:
        x = urlsplit(u)
        return x.scheme == "https" and bool(x.netloc) and not x.username and not x.password
    except (TypeError, ValueError):
        return False


def evaluate(p):
    """HOLD on incomplete evidence, ITERATE if under benchmark, else REVIEW_REQUIRED."""
    missing = []
    def check(ok, reason):
        if not ok:
            missing.append(reason)
    if not isinstance(p, dict):
        return {"status": "HOLD", "issues": ["packet must be object"], "release_authorized": False, "scores": None}
    check(p.get("schema") == "WTBW-1.0", "wrong schema")
    check(bool(re.fullmatch(r"PRY-[1-9][0-9]*", str(p.get("issue", "")))), "canonical issue required")
    check(bool(p.get("owner")) and bool(p.get("user_job")) and bool(p.get("failure")), "owner/job/failure required")
    check(bool(p.get("advantage")) and bool(p.get("do_not_copy")), "originality advantage and do-not-copy required")
    artifact = p.get("artifact") if isinstance(p.get("artifact"), dict) else {}
    check(bool(artifact.get("repository")) and bool(C.fullmatch(str(artifact.get("base_sha", "")))), "repository/base SHA required")
    proto = p.get("protocol") if isinstance(p.get("protocol"), dict) else {}
    fixed = proto.get("fixture_sha256")
    check(bool(H.fullmatch(str(fixed or ""))), "frozen fixture SHA256 required")
    check(bool(proto.get("preregistered_at")) and bool(proto.get("method")), "preregistration and method required")
    check(proto.get("blinded") is True, "blinded comparison required")
    kind = proto.get("kind")
    n = proto.get("sample_count")
    judges = proto.get("judges")
    check(kind in ("objective", "editorial"), "invalid evaluation kind")
    check(type(n) is int and n >= (20 if kind == "objective" else 3), "insufficient test samples")
    check(type(judges) is int and judges >= (3 if kind == "editorial" else 1), "insufficient independent judges")
    margin = proto.get("minimum_margin")
    check(type(margin) in (int, float) and math.isfinite(margin) and 0 <= margin <= 20, "invalid preregistered margin")
    weights = proto.get("weights") if isinstance(proto.get("weights"), dict) else {}
    valid_weights = bool(weights) and set(weights).issubset(METRICS) and all(type(v) in (int,float) and math.isfinite(v) and v > 0 for v in weights.values())
    check(valid_weights and math.isclose(sum(v for v in weights.values() if type(v) in (int,float) and math.isfinite(v)),100,abs_tol=1e-6), "weights must be positive finite and total 100")
    gates = p.get("gates") if isinstance(p.get("gates"), dict) else {}
    for g in GATES:
        check(gates.get(g) == "pass", "hard gate missing: " + g)
    check(gates.get("human_release_approval") in ("pending","denied","approved") and gates.get("production_deployed") is not True, "approval/deployment state invalid")
    review = p.get("review") if isinstance(p.get("review"), dict) else {}
    check(bool(review.get("builder")) and bool(review.get("verifier")) and review.get("builder") != review.get("verifier"), "independent verifier required")
    check(weburl(review.get("evidence_url")), "independent reviewer evidence required")
    check(bool(p.get("rollback")) and bool(p.get("next_experiment")), "rollback and next experiment required")
    seen, group, measured = set(), {"baseline":0,"candidate":0,"direct":0,"lateral":0}, {}
    entries = p.get("entries") if isinstance(p.get("entries"), list) else []
    for ix,e in enumerate(entries):
        tag = "entry[%d]" % ix
        if not isinstance(e,dict):
            missing.append(tag + " invalid");continue
        role,name = e.get("role"),e.get("name")
        if role not in group:
            missing.append(tag + " invalid role");continue
        group[role] += 1
        check(type(name) is str and bool(name), tag+" missing name")
        if type(name) is str:
            check(name not in seen,tag+" duplicate name")
            seen.add(name)
        source = e.get("source") if isinstance(e.get("source"),dict) else {}
        check(weburl(source.get("url")) and bool(source.get("checked_at")) and bool(source.get("mechanism")) and bool(source.get("rights_note")),tag+" invalid source/rights evidence")
        receipt = e.get("receipt") if isinstance(e.get("receipt"),dict) else {}
        check(bool(H.fullmatch(str(receipt.get("artifact_sha256", "")))) and receipt.get("fixture_sha256") == fixed and bool(receipt.get("run_id")) and weburl(receipt.get("evidence_url")),tag+" inconsistent or missing frozen test receipt")
        scores = e.get("scores")
        okay = isinstance(scores,dict) and set(scores)==set(weights) and all(type(v) in (int,float) and math.isfinite(v) and 0<=v<=100 for v in scores.values())
        check(okay,tag+" invalid comparable scores")
        if okay and valid_weights and type(name) is str:
            measured[name] = (role, round(sum(scores[k] * weights[k]/100 for k in weights),3))
    check(group["baseline"] == 1 and group["candidate"] == 1 and group["direct"] >= 2 and group["lateral"] >= 1, "require one baseline/candidate, two direct peers, one lateral")
    result={"status":"HOLD", "issues":missing, "scores":None, "release_authorized":False,
            "caution":"Only structural consistency. URLs, real tests, receipts, signatures, reviewer independence, rights and video/device facts require separate trusted verification."}
    if missing:
        return result
    baseline=next(x for role,x in measured.values() if role=="baseline")
    candidate=next(x for role,x in measured.values() if role=="candidate")
    champion=max(x for role,x in measured.values() if role in ("direct","lateral"))
    result["scores"]={"baseline":baseline,"candidate":candidate,"best_reference":champion,"delta_to_best":round(candidate-champion,3),"minimum_margin":margin}
    if candidate-champion < margin or candidate-baseline < margin:
        result["status"]="ITERATE"
        result["issues"]=["Candidate not measurably above frozen comparators, fix same original artifact and retest."]
    else:
        result["status"]="REVIEW_REQUIRED"
        result["issues"]=["Review independently before any founder release approval. No automatic deployment."]
    return result


def main():
    a=argparse.ArgumentParser(description="Pryntor WTB&W offline structural benchmark review")
    a.add_argument("packet",type=Path)
    args=a.parse_args()
    try:
        p=json.loads(args.packet.read_text(encoding="utf-8"))
        r=evaluate(p)
    except (OSError, ValueError) as exc:
        r={"status":"HOLD","issues":["unreadable packet: "+str(exc)],"release_authorized":False}
    print(json.dumps(r,indent=2,sort_keys=True))
    return 2 if r["status"]=="HOLD" else 0

if __name__=="__main__":
    sys.exit(main())
