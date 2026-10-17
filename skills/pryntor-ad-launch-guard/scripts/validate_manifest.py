#!/usr/bin/env python3
"""Offline Pryntor ad-manifest preflight. NO vendor API calls or permission to spend."""
import argparse
import ipaddress
import json
import re
import sys
from urllib.parse import urlsplit, parse_qs

TOP = {"mode","approval_status","live","spend_enabled","budget","tenant","account_id","objective","campaign_name","adset_name","ads"}
AD = {"name","publish","enhancements_enabled","approved_rights","cta","placements","media","url"}
OBJECTIVES = {"traffic","leads","sales","awareness"}
PLACEMENTS = {"feed","reels","stories"}
UTMS = ("utm_source","utm_medium","utm_campaign")

def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["Manifest must be an object"]
    extra = set(data) - TOP
    if extra: errors.append("Unexpected top-level keys: "+",".join(sorted(extra)))
    if data.get("mode") != "dry_run": errors.append("Mode must be dry_run")
    if data.get("approval_status") not in ("test_only","draft_only"): errors.append("Approval must be test_only or draft_only")
    if data.get("live") is not False: errors.append("Live must be false")
    if data.get("spend_enabled") is not False: errors.append("Spend must be false")
    if isinstance(data.get("budget"), bool) or data.get("budget") != 0: errors.append("Budget must be zero")
    if not isinstance(data.get("tenant"), str) or not re.fullmatch(r"[a-z][a-z0-9-]{2,39}",data["tenant"]): errors.append("Tenant must be safe slug")
    if not isinstance(data.get("account_id"), str) or not re.fullmatch(r"test_[A-Za-z0-9_-]{3,64}",data["account_id"]): errors.append("Account must use synthetic test_ ID")
    if not isinstance(data.get("objective"), str) or data["objective"] not in OBJECTIVES: errors.append("Unsupported objective")
    for k in ("campaign_name","adset_name"):
        if not isinstance(data.get(k),str) or not data[k].strip() or len(data[k]) > 160: errors.append(k+" invalid")
    ads = data.get("ads")
    if not isinstance(ads,list) or not 1 <= len(ads) <= 50:
        return errors + ["1-50 ads required"]
    names=set()
    for n,a in enumerate(ads,1):
        p=f"ads[{n}]"
        if not isinstance(a,dict):
            errors.append(p+" must be object")
            continue
        extra=set(a)-AD
        if extra: errors.append(p+" unexpected keys: "+",".join(sorted(extra)))
        name=a.get("name")
        if not isinstance(name,str) or not name.strip() or len(name)>160: errors.append(p+" invalid name")
        elif name in names: errors.append(p+" duplicate name")
        else: names.add(name)
        for k in ("publish","enhancements_enabled"):
            if a.get(k) is not False: errors.append(p+" "+k+" must be false")
        if a.get("approved_rights") is not True: errors.append(p+" rights must be approved")
        if a.get("cta") not in ("LEARN_MORE","SHOP_NOW","SIGN_UP"): errors.append(p+" CTA invalid")
        places=a.get("placements")
        if not isinstance(places,list) or not places or any(not isinstance(x,str) or x not in PLACEMENTS for x in places): errors.append(p+" placements invalid")
        media=a.get("media")
        if not isinstance(media,list) or not media or any(not isinstance(x,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./-]{0,240}\.(?:png|jpe?g|mp4)",x) or any(segment in (".","..") for segment in x.split("/")) for x in media): errors.append(p+" media invalid")
        url=a.get("url")
        if not isinstance(url,str):
            errors.append(p+" url must be HTTPS")
            continue
        try:
            parsed=urlsplit(url)
            host=parsed.hostname or ""
            if (parsed.scheme!="https" or parsed.username or parsed.password or not host or
                not re.fullmatch(r"[A-Za-z0-9.-]+",host) or "." not in host or
                host.endswith((".local",".internal")) or parsed.port not in (None,443)):
                errors.append(p+" public HTTPS URL required")
            try:
                if not ipaddress.ip_address(host).is_global: errors.append(p+" public IP required")
            except ValueError:
                pass
            qs=parse_qs(parsed.query)
            for k in UTMS:
                vals=qs.get(k,[])
                if len(vals)!=1 or not vals[0].strip() or len(vals[0])>160 or any(ord(c)<32 for c in vals[0]):
                    errors.append(p+" invalid or ambiguous "+k)
        except ValueError:
            errors.append(p+" invalid URL")
    return errors

def main():
    ap=argparse.ArgumentParser(description="Offline synthetic manifest validator; no ad calls")
    ap.add_argument("manifest")
    args=ap.parse_args()
    try:
        with open(args.manifest,encoding="utf-8") as handle: data=json.load(handle)
        errors=validate(data)
    except (OSError,ValueError) as exc: errors=[str(exc)]
    print(json.dumps({"status":"FAIL" if errors else "PASS_OFFLINE_ONLY","errors":errors},indent=2))
    return 1 if errors else 0

if __name__=="__main__":
    sys.exit(main())
