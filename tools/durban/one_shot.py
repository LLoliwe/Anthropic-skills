#!/usr/bin/env python3
"""ONE anonymous free Space request for an original Durban four-second character shot.

Fail closed: no paid inference, tokens, top-ups, retries, child/customer content.
Never convert a *post-download local QA error* into a false provider failure.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time

SPACE = 'Lightricks/LTX-2.5'
PROMPT = (
    'One continuous 4-second highly cinematic 3D animated character film shot, SOUTH AFRICA, '
    'Durban Golden Mile beachfront promenade at the Indian Ocean during beautiful warm sunrise. '
    'A SMALL ORIGINAL FICTIONAL BLUE FLUFFY CREATURE with soft textile fur, round peach-colored face, '
    'wide kind dark eyes, two tiny articulated hands, and two short legs. '
    'The creature is walking along the beachfront, lifts and plants its left foot with believable body weight, '
    'turns its head toward breaking Indian Ocean waves, blinks in wonder, then smiles and waves toward the camera. '
    'Actual independently articulated hands, legs, head, face and plush fur, physical ground contact and shadow. '
    'Clearly recognizable large white sweeping arch of Moses Mabhida Stadium on the distant Durban skyline '
    'behind the palms and beach, not Cape Town, no Table Mountain. '
    'Purposeful cinema camera low near character eyeline tracks left to right through three-dimensional foreground '
    'palms, dollying closer then arcing 20 degrees around the moving character; natural parallax and depth. '
    'Handcrafted premium studio-quality feature animation look, physically lit soft plush fibers, '
    'natural expressive acting, consistent character identity, detailed authentic environment, golden-hour reflections, '
    '16:9 widescreen framing. No subtitles, no text, no jump cuts, no still photo movement, no slideshow, '
    'no popular characters or copyrighted designs, no hallucinated extra feet, no morphing, no logos.'
)

def one_path(v):
    if isinstance(v, str): return Path(v)
    if isinstance(v, dict):
        for k in ('video', 'path', 'name'):
            if k in v and v[k]: return one_path(v[k])
    if isinstance(v, (tuple,list)) and v: return one_path(v[0])
    raise ValueError('Unsupported returned video descriptor')

def write(d, **changes):
    data={'provider': SPACE, 'status': 'BLOCKED', 'cash_spend_authorized': False, 'paid_api_invoked': False,
          'human_approved': False,'generation_count':0, **changes}
    (d/'status.json').write_text(json.dumps(data, indent=2))
    print('STATUS:',json.dumps(data),flush=True)
    return data

def main():
    dest=Path(os.environ.get('OUTPUT_DIR', 'durban_output'))
    dest.mkdir(parents=True,exist_ok=True)
    prohibited=[name for name in ('HF_TOKEN','HUGGING_FACE_HUB_TOKEN','HUGGINGFACEHUB_API_TOKEN',
                'OPENAI_API_KEY','RUNWAY_API_KEY') if os.getenv(name)]
    if prohibited:
        write(dest, reason='Token detected in environment; anonymous-only run prohibited', token_names=prohibited)
        return 0
    (dest/'PROMPT.txt').write_text(PROMPT)
    t=time.monotonic()
    try:
        from gradio_client import Client
        client=Client(SPACE,verbose=False,httpx_kwargs={'timeout':90.0})
        print('One free anonymous demo request; no retry and no wallet.',flush=True)
        result=client.predict(PROMPT,None,512,768,4.0,42,'conv',False,False,False,api_name='/run')
        src=one_path(result[0] if isinstance(result,(list,tuple)) else result)
        if not src.is_file() or src.stat().st_size < 25000:
            raise RuntimeError('The public demo did not return a real MP4 file')
        out=dest/'PRYNTOR_DURBAN_GOLDEN_MILE_NEW_ANIMATION.mp4'
        shutil.copyfile(src,out)
        if out.stat().st_size < 25000 or b'ftyp' not in out.read_bytes()[:64]:
            raise RuntimeError('Returned asset is not a plausible MP4 file')
        sha=hashlib.sha256(out.read_bytes()).hexdigest()
        # No ffprobe dependency; the returned asset is preserved even if later QA is unavailable.
        write(dest,status='RENDERED_UNREVIEWED',reason='Demo supplied a genuine MP4 file; independent motion QA required',
              generation_count=1, video=out.name,bytes=out.stat().st_size,sha256=sha,
              elapsed_seconds=round(time.monotonic()-t,1))
    except Exception as exc:
        write(dest,status='BLOCKED',reason=f'{type(exc).__name__}: {str(exc)[:550]}',
              elapsed_seconds=round(time.monotonic()-t,1))
    return 0

if __name__=='__main__':sys.exit(main())