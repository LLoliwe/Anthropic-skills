"""Verify contiguous native 3D render frames before encode. No slideshow/movie cheats.
Technical checks are necessary but insufficient for aesthetic release approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat


def sha256(p):
    d=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            d.update(chunk)
    return d.hexdigest()


def check(folder, width, expected=49):
    root=Path(folder)
    paths=[root/f'motion_{n:03}.png' for n in range(1,expected+1)]
    assert len(paths)==expected and all(x.is_file() for x in paths),'missing or incomplete actual CGI frames'
    prev=None;deltas=[];first=None;last=None;checks=[]
    for i,path in enumerate(paths):
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            im.load()
            assert im.size==(width,round(width*9/16)), (path,im.size)
            rgb=im.convert('RGB')
            small=rgb.resize((128,72))
            assert rgb.entropy()>2.2, f'Empty/blank frame {i+1}'
            if prev is not None:
                channel_mean=ImageStat.Stat(ImageChops.difference(prev,small)).mean
                d=sum(channel_mean)/3
                deltas.append(d)
            else: first=small.copy()
            prev=small
            checks.append({'frame':i+1,'sha256':sha256(path),'bytes':path.stat().st_size})
    last=prev
    total=sum(ImageStat.Stat(ImageChops.difference(first,last)).mean)/3
    assert total>2.0, f'No appreciable real camera move: {total}'
    assert min(deltas)>0.005, f'Duplicated frozen frame: {min(deltas)}'
    assert max(deltas)<25.0, f'Unexpected abrupt cut/flash: {max(deltas)}'
    evidence={'expected_frames':expected,'frame_width':width,'fps':16,'shot_length_seconds':expected/16,'source':'49 actual consecutive 3D-rendered frames','frames':checks,'camera_first_last_delta':round(total,3),'min_adjacent_delta':round(min(deltas),3),'max_adjacent_delta':round(max(deltas),3),'acceptance':'TECHNICAL ONLY — original creative/artistic review PENDING'}
    (root/'motion_qa.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('CONTIGUOUS_3D_MOTION_QA_PASS',total,min(deltas),max(deltas))

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--folder',type=Path,default=Path('output'));pa.add_argument('--width',type=int,default=576)
    args=pa.parse_args();check(args.folder,args.width)
