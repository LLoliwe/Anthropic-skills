#!/usr/bin/env python3
"""Reproducible real upstream Earshot v0.2 acceptance. Original synthetic fixtures only.
Source pinned by cloud workflow; no user media, keys, network LLMs or paid services.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import wave

OUT = Path(os.environ.get("EARSHOT_PROOF_DIR", "/tmp/pryntor-earshot-proof"))
OUT.mkdir(parents=True, exist_ok=True)

def record(name, data):
    with wave.open(str(OUT/name), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        import struct
        w.writeframes(struct.pack("<"+"h"*len(data), *data))

def fixture():
    n=16000
    def clip(i):
        t=i/n
        decay=math.exp(-11*t)
        attack=min(1,t*380)
        return round(32767*0.46*attack*decay*(0.75*math.sin(2*math.pi*784*t)+0.25*math.sin(2*math.pi*1176*t)))
    ref=[clip(i) for i in range(n)]
    record("original-ding.wav",ref)
    movie=[]
    for j in range(n*4):
        t=j/n
        ix=j%n
        s=round(0.07*32767*math.sin(2*math.pi*110*t))
        if t<3.5 and ix < n: s+=int(0.3*ref[ix]) if (j//n)%2==0 else 0
        movie.append(max(-32768,min(32767,s)))
    record("original-demo-mix.wav",movie)
    cmd=["ffmpeg","-y","-nostdin","-hide_banner","-loglevel","error","-f","lavfi","-i",
        "color=c=0x182030:s=480x270:r=24:d=4","-i",str(OUT/"original-demo-mix.wav"),
        "-shortest","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",str(OUT/"original-demo.mp4")]
    subprocess.run(cmd,check=True)
    report={"fixture":"original 784Hz and 1176Hz decaying ding with an original 4s video mix",
        "license":"author-generated synthetic, no third-party audio or footage",
        "ding_sha256":hashlib.sha256((OUT/"original-ding.wav").read_bytes()).hexdigest(),
        "video_sha256":hashlib.sha256((OUT/"original-demo.mp4").read_bytes()).hexdigest()}
    (OUT/"fixture.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))

def run_cli(*args, name):
    proc=subprocess.run([sys.executable,"-m","earshot",*args],text=True,capture_output=True,timeout=480)
    (OUT/f"{name}.log").write_text(proc.stdout[-9000:]+"\nSTDERR:\n"+proc.stderr[-5000:])
    if proc.returncode:
        raise RuntimeError(f"{name} exit={proc.returncode}: {proc.stderr[-1800:]}")
    return proc.stdout

def fit():
    run_cli("fit",str(OUT/"original-ding.wav"),"--kind","modal","--fast","-o",
            str(OUT/"ding_recipe.py"),"--json","--out",str(OUT/"fit.json"),name="fit")
    code=OUT/"ding_recipe.py"; wav=OUT/"ding_recipe.wav"; info=OUT/"fit.json"
    if not code.is_file() or not wav.is_file() or not info.is_file(): raise AssertionError("source and WAV not created")
    if len(code.read_text())<100 or wav.stat().st_size<2500: raise AssertionError("empty recipe or sound")
    command=subprocess.run([sys.executable,str(code),"4",str(OUT/"variant-seed4.wav")],
                           capture_output=True,text=True,timeout=90)
    if command.returncode: raise RuntimeError(command.stderr[-1000:])
    variation=OUT/"variant-seed4.wav"
    if not variation.is_file() or variation.stat().st_size<2500: raise AssertionError("recipe did not independently render")
    summary={"code_created":True,"render_created":True,"independent_code_re_render":True,
             "source_file_bytes":code.stat().st_size,"wav_bytes":wav.stat().st_size,
             "variant_bytes":variation.stat().st_size,"upstream_report":json.loads(info.read_text())}
    (OUT/"fit-validation.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print("EARSHOT_FIT_REAL_PASS")

async def mcp():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    parms=StdioServerParameters(command=sys.executable,args=["-m","earshot","mcp"],
                               env={**os.environ,"EARSHOT_OFFLINE":"1","EARSHOT_THREADS":"2"})
    async with stdio_client(parms) as (reader,writer):
        async with ClientSession(reader,writer) as session:
            await session.initialize()
            tools=await session.list_tools()
            names=[t.name for t in tools.tools]
            expected={"measure","critique","describe","timeline","doctor"}
            if not expected.issubset(set(names)):raise AssertionError(f"missing advertised tools {expected-set(names)}")
            response=await session.call_tool("measure",{"file":str(OUT/"original-ding.wav")})
            if response.isError: raise RuntimeError("MCP measure returned error: "+str(response.content)[:800])
            text="\n".join(str(getattr(c,"text", "")) for c in response.content)
            if not text.strip():raise AssertionError("MCP measure no output")
            summary={"transport":"stdio","handshake":True,"tools":names,"tools_count":len(names),
                     "measure_called":True,"response_excerpt":text[:1200],
                     "note":"MCP server exposes analysis tools; Forge/Fit are CLI/Python, not MCP tools."}
            (OUT/"mcp-validation.json").write_text(json.dumps(summary,indent=2)+"\n")
            print("EARSHOT_MCP_REAL_PASS",len(names))

def critique():
    run_cli("doctor","--load","--json","--out",str(OUT/"doctor.json"),name="doctor-loaded")
    report=json.loads((OUT/"doctor.json").read_text())
    run_cli("critique",str(OUT/"original-demo.mp4"),"--json","--out",
            str(OUT/"critique.json"),name="critique-model")
    review=json.loads((OUT/"critique.json").read_text())
    if not isinstance(review,dict) or not review.get("metrics"):
        raise AssertionError("No non-empty real scorecard metrics")
    if "verdict" not in review:raise AssertionError("No verdict reported")
    summary={"doctor":report,"critique_verdict":review.get("verdict"),
             "critique_score":review.get("score"),"metric_count":len(review.get("metrics",{})),
             "uses_model_path":"critique without --fast, intended AST and realness inference",
             "limitations":"This is a synthetic film test, not human listening or rights clearance."}
    (OUT/"critique-validation.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print("EARSHOT_CRITIQUE_REAL_PASS",summary["metric_count"])

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("phase",choices=["fixture","fit","mcp","critique"])
    choice=ap.parse_args().phase
    {"fixture":fixture,"fit":fit,"mcp":lambda:asyncio.run(mcp()),"critique":critique}[choice]()
