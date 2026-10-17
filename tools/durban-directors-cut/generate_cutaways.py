#!/usr/bin/env python3
"""Two strictly free anonymous LTX-2.5 shots for Durban film, with reference.
No paid keys / billing. Each shot one request only, no retries. Every output
preserved before QA. Failures reported, not fabricated.
"""
from __future__ import annotations
import base64,hashlib,json,os,shutil,sys,time
from pathlib import Path

SPACE='Lightricks/LTX-2.5'
OUT=Path('render_out'); OUT.mkdir(parents=True,exist_ok=True)
SOURCE=Path(__file__).parent
PROMPTS={
'B_REACTION':(
 'Use the attached input image as the first frame and LOCK the identity and facial structure of the EXACT same original little blue plush-furred character with large soft peach ears, peach warm face, dark brown eyes, royal blue tufted fur, dark blue little romper-like body, little peach hands and bare feet. Film a SINGLE continuous 4-second action on the Durban Golden Mile beachfront beside warm Indian Ocean surf, recognizable pale arc of Moses Mabhida Stadium and South African coastal palms distant in background, same sunrise color and sun orientation as the image. Professional nuanced character acting with a complete purposeful beat: the blue character notices a tiny pearlescent shell near their feet; eyes track downward and blink; knees flex with weight, head and torso genuinely bend with anticipation, small peach hand reaches to pick up the shell while feet stay grounded; then the creature smiles, eyes light up, holding shell up with evident joy for camera. Genuine moving limbs, individual finger and ear motion and proper tactile fur motion. Camera makes one small physically plausible low-angle 25-degree arc around character with true changing 3D parallax, shallow depth of field favoring face and shell, warm reflected practical light. 35mm cinema lens, handcrafted 3D animated family film quality, motivated motion, tactile naturalism. One coherent shot, no cuts, no additional creatures, no balloons, no shape/identity changes, no slidy whole-frame zoom, no titles, NO forced dialogue. Sound only delicate surf and tiny foot/shell pickup foley.'),
'A_BEACH':(
 'Single 4-second high-end cinematic animated film establishing shot of Durban South Africa Golden Mile beachfront at dawn. Camera starts only a few centimeters above wet bronze-gold sand, running smoothly laterally toward the horizon as a real Indian Ocean wave rolls in and washes around a small pearly seashell close to the lens, causing sand grains and water foam to shift independently in accurate physical motion. Low wide 24mm anamorphic lens, tasteful depth of field, unusual dramatic foreground and layered parallax; camera tilts up very gently to reveal Durban beachfront palms and a recognizable white arch of Moses Mabhida Stadium in the distance, golden sky. A pair of tiny fresh plush-foot footprints in damp sand leads away from camera as a visual hook for next shot. Meaningful motion in surf, reflections, gull at far horizon. Clean art-directed premium original 3D animated film world, painterly but photoreal materials, no people, no tiny blue creature in this opening shot, no text, no logo, no montage, no still photograph movements. Synchronize audible ocean rush, soft wind and distant gull cries, no music or narration.')}


def status(data):
 (OUT/'STATUS.json').write_text(json.dumps(data,indent=2));print('PROOF_STATUS:',json.dumps(data),flush=True)

def path_of(v):
 if isinstance(v,str):return Path(v)
 if isinstance(v,dict):
  for k in ('video','path','name'):
   if v.get(k):return path_of(v[k])
 if isinstance(v,(tuple,list)) and v:return path_of(v[0])
 raise TypeError(f'No file path in {type(v)}')


def main():
 forbidden=[k for k in ['HF_TOKEN','HUGGING_FACE_HUB_TOKEN','HUGGINGFACEHUB_API_TOKEN','OPENAI_API_KEY','RUNWAY_API_KEY','ELEVENLABS_API_KEY'] if os.getenv(k)]
 manifest={'spent_cash':False,'provider':SPACE,'generation_attempts':0,'clips':{},'blocked':[],'source_image_name':'actor_anchor.jpg'}
 if forbidden:
  manifest['blocked'].append('secret present; anonymous-only failure');status(manifest);return 0
 raw=base64.b64decode((SOURCE/'actor_anchor.b64').read_text())
 img=OUT/'actor_anchor.jpg';img.write_bytes(raw)
 from gradio_client import Client,handle_file
 try:cl=Client(SPACE,verbose=False,httpx_kwargs={'timeout':100.0})
 except Exception as ex:
  manifest['blocked'].append('Connection: '+repr(ex)[:400]);status(manifest);return 0
 # Critical hero performance first; one free request per shot, do not retry.
 for key in ('B_REACTION','A_BEACH'):
  manifest['generation_attempts']+=1
  (OUT/(key+'_PROMPT.txt')).write_text(PROMPTS[key],encoding='utf-8')
  t=time.monotonic()
  try:
   src_ref=handle_file(str(img)) if key=='B_REACTION' else None
   result=cl.predict(PROMPTS[key],src_ref,512,768,4.0,42,'conv',False,False,False,api_name='/run')
   path=path_of(result[0] if isinstance(result,(list,tuple)) else result)
   if not path.is_file() or path.stat().st_size<25000:raise RuntimeError('No completed MP4 received')
   dst=OUT/(key+'.mp4');shutil.copyfile(path,dst)
   if b'ftyp' not in dst.read_bytes()[:64]:raise ValueError('not plausibly an MP4')
   manifest['clips'][key]={'status':'RENDERED_UNREVIEWED','filename':dst.name,'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'elapsed_s':round(time.monotonic()-t,1)}
   status(manifest)
  except Exception as ex:
   manifest['blocked'].append(f'{key}: {type(ex).__name__}: {str(ex)[:400]}')
   status(manifest)
   # If quota limits the first call, stop rather than run a second.
   if key=='B_REACTION':break
 return 0

if __name__=='__main__':sys.exit(main())