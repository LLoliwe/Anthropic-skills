#!/usr/bin/env python3
"""Pryntor video evidence intake R0: local deterministic metadata, not AI reasoning.
Requires ffprobe; optional OpenCV for sampled local JPEGs. Does not call network.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone

SCHEMA = 'pryntor.video-evidence.v1'
TIERS = ('public', 'internal', 'restricted')
RIGHTS = ('owned', 'licensed', 'reference-only', 'unknown')

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def get_video_metadata(path):
    p=Path(path)
    if not p.is_file(): raise ValueError('video file does not exist')
    cmd=['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]
    try: proc=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=30)
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired,FileNotFoundError) as e: raise ValueError('ffprobe unavailable or unsupported video file') from e
    try: payload=json.loads(proc.stdout)
    except (json.JSONDecodeError,TypeError) as e: raise ValueError('invalid media metadata') from e
    video=next((s for s in payload.get('streams',[]) if s.get('codec_type')=='video'),None)
    if video is None:raise ValueError('no video stream')
    fps=video.get('avg_frame_rate') or '0/1'
    try:
        n,d=map(float,fps.split('/')); rate=round(n/d,4) if d and n else None
    except (ValueError,ZeroDivisionError):rate=None
    duration=float(payload.get('format',{}).get('duration') or video.get('duration') or 0)
    if duration<=0:raise ValueError('video duration unavailable')
    return {'duration_seconds':round(duration,4),'fps':rate,
            'width':int(video.get('width') or 0),'height':int(video.get('height') or 0),
            'video_codec':video.get('codec_name'),'audio_present':any(s.get('codec_type')=='audio' for s in payload.get('streams',[]))}

def sample_seconds(duration, interval, max_frames):
    if not all(math.isfinite(x) for x in (duration,interval)) or duration<=0 or interval<=0 or max_frames<1:
        raise ValueError('duration/interval/max_frames invalid')
    if max_frames==1: return [0.0]
    last=round(max(0.0,duration-0.1),3)
    # Cover the complete clip even when the requested interval exceeds the frame budget.
    wanted=[0.0]
    t=interval
    while t<last and len(wanted)<max_frames:
        wanted.append(round(t,3));t+=interval
    if last>wanted[-1]:wanted.append(last)
    if len(wanted)<=max_frames:return wanted
    return [round(i*last/(max_frames-1),3) for i in range(max_frames)]

def sample_frames(path,out,times):
    # Sampled frames alone cannot establish motion or causal facts.
    try:import cv2
    except ImportError as e:raise ValueError('OpenCV is required for optional local frame extraction') from e
    cap=cv2.VideoCapture(str(path)); written=[]
    try:
        if not cap.isOpened():raise ValueError('video decoder unavailable')
        for i,t in enumerate(times):
            cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
            ok,frame=cap.read()
            if not ok:continue
            frame_path=out / f'frame_{i:03d}_{int(t*1000):08d}ms.jpg'
            if not cv2.imwrite(str(frame_path),frame):raise ValueError('could not write sampled frame')
            written.append({'time_seconds':t,'path':frame_path.name,'sha256':sha256(frame_path)})
    finally:cap.release()
    return written

def intake(path,output_dir,owner,rights,privacy,frames=False,interval=1,max_frames=24):
    if not owner.strip():raise ValueError('source owner must be set')
    if rights not in RIGHTS or privacy not in TIERS:raise ValueError('unsupported rights/privacy setting')
    p=Path(path).resolve(); out=Path(output_dir).resolve()
    if not p.is_file():raise ValueError('video not found')
    meta=get_video_metadata(p)
    if not out.exists():out.mkdir(parents=True,mode=0o700)
    if not out.is_dir():raise ValueError('output must be a directory')
    # Private by default. Tighten the directory permissions before writing evidence.
    out.chmod(out.stat().st_mode & 0o700)
    times=sample_seconds(meta['duration_seconds'],interval,max_frames)
    generated=sample_frames(p,out,times) if frames else []
    manifest={'schema':SCHEMA,'created_utc':datetime.now(timezone.utc).isoformat(),
         'source':{'filename':p.name,'sha256':sha256(p),'owner':owner,'rights':rights,
                   'privacy_tier':privacy,'third_party_upload_allowed':False},
         'technical_metadata':meta,
         'sampling':{'mode':'local_frame_sampling' if frames else 'timestamps_only','requested_times_seconds':times,'frames':generated},
         'observations':[],'hypotheses':[],'human_review':{'status':'not_reviewed'},
         'limits':['This is technical intake, NOT a model interpretation or independent review.',
                   'Frame samples can miss transitions, actions, visual details and audio events.',
                   'No external upload has occurred.']}
    fd=os.open(out/'evidence.json',os.O_WRONLY | os.O_CREAT | os.O_TRUNC,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as stream:
        stream.write(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    return manifest

def validate(evidence):
    if evidence.get('schema')!=SCHEMA:raise ValueError('invalid evidence schema')
    src=evidence.get('source',{}); meta=evidence.get('technical_metadata',{})
    digest=src.get('sha256','')
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('invalid source SHA256')
    if src.get('third_party_upload_allowed') is not False:
        raise ValueError('third-party permission cannot be self-certified')
    if meta.get('duration_seconds',0)<=0:raise ValueError('duration absent')
    for o in evidence.get('observations',[]):
        if o.get('kind')!='observed' or not o.get('claim'):raise ValueError('observation must be marked observed with claim')
        if not isinstance(o.get('time_seconds'),(int,float)) or not 0<=o['time_seconds']<=meta['duration_seconds']:
            raise ValueError('observation timestamp invalid')
        if not o.get('evidence_frames') or not isinstance(o['evidence_frames'],list):raise ValueError('observation must cite source frames')
        allowed={f['path'] for f in evidence.get('sampling',{}).get('frames',[])}
        if any(x not in allowed for x in o['evidence_frames']):raise ValueError('observation cites missing source frame')
    for h in evidence.get('hypotheses',[]):
        if h.get('kind')!='hypothesis' or not h.get('claim') or not h.get('limitations'):
            raise ValueError('inferences require explicit hypothesis marking and limitations')
    if evidence.get('human_review',{}).get('status') not in ('not_reviewed','approved','rejected'):
        raise ValueError('unknown human review status')
    return True

def main():
    p=argparse.ArgumentParser(description='Pryntor offline video evidence intake (no AI model or network)')
    sub=p.add_subparsers(dest='cmd',required=True)
    i=sub.add_parser('intake');i.add_argument('video');i.add_argument('--out',required=True)
    i.add_argument('--owner',required=True);i.add_argument('--rights',choices=RIGHTS,default='unknown')
    i.add_argument('--privacy',choices=TIERS,default='restricted')
    i.add_argument('--frames',action='store_true')
    i.add_argument('--interval',type=float,default=1);i.add_argument('--max-frames',type=int,default=24)
    v=sub.add_parser('validate');v.add_argument('json_file')
    a=p.parse_args()
    try:
        if a.cmd=='intake':
            result=intake(a.video,a.out,a.owner,a.rights,a.privacy,a.frames,a.interval,a.max_frames)
            print(json.dumps({'result':'LOCAL_INTAKE_ONLY','sha256':result['source']['sha256'],'duration_seconds':result['technical_metadata']['duration_seconds'],'frames':len(result['sampling']['frames']),'evidence':str(Path(a.out)/'evidence.json')}))
        else:
            validate(json.loads(Path(a.json_file).read_text(encoding='utf8')))
            print('EVIDENCE_STRUCTURE_VALID; semantic factual accuracy NOT established')
    except (ValueError,OSError) as e:p.exit(2,f'ERROR: {e}\n')
if __name__=='__main__':main()
