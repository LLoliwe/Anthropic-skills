"""Independent (non-Blender) QA: full decode, editable .blend, variation, provenance.
Only technical tests. No synthetic metric can certify world-class visual design.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):
            h.update(part)
    return h.hexdigest()


def verify(output, width):
    output=Path(output)
    source=output/'red_hour_gallery_editable.blend'
    assert source.is_file(), 'Missing Blender edit source'
    assert source.read_bytes()[:7]==b'BLENDER', 'Invalid Blender file header'
    prov=json.loads((output/'render_provenance.json').read_text())
    assert prov['external_image_video_api_calls']==0
    assert prov['third_party_models_or_textures']==0
    assert prov['human_approval'].startswith('PENDING')
    evidence={'render_source':{'file':source.name,'sha256':digest(source),'bytes':source.stat().st_size},'frames':[]}
    arrays=[]
    for f in (1,25,49):
        p=output/f'red_hour_f{f:03}.png'
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            im.load()
            assert im.size==(width,round(width*9/16)),(im.size,width)
            rgb=im.convert('RGB')
            e=rgb.entropy()
            sd=ImageStat.Stat(rgb).stddev
            assert e>2.0 and max(sd)>9, f'Blank render frame {f} entropy={e} stddev={sd}'
            arrays.append(rgb.copy())
        evidence['frames'].append({'file':p.name,'sha256':digest(p),'bytes':p.stat().st_size,'entropy':round(e,2),'stdev':[round(x,2) for x in sd]})
    delta=ImageStat.Stat(ImageChops.difference(arrays[0], arrays[2])).mean
    assert sum(delta)/3>2.5, f'Camera no visible movement: {delta}'
    evidence['frame_01_to_49_avg_change_rgb']=delta
    evidence['visual_artistic_approval']='NOT TESTED — HUMAN REVIEW REQUIRED'
    evidence['passes']=len(evidence['frames'])+3
    (output/'QA.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))
    return evidence


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path('output'));ap.add_argument('--width',type=int,default=960)
    a=ap.parse_args();verify(a.output,a.width)
