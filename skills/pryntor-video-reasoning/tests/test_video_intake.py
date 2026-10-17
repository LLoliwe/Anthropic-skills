import hashlib
import json
import subprocess
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from video_intake import intake, get_video_metadata, sha256, sample_seconds, validate

@pytest.fixture
def video(tmp_path):
    target=tmp_path/'test.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i','color=c=red:s=64x64:r=5:d=1','-f','lavfi','-i','color=c=green:s=64x64:r=5:d=1','-filter_complex','[0:v][1:v]concat=n=2:v=1:a=0[out]','-map','[out]','-c:v','mpeg4',str(target)],check=True,timeout=30)
    return target

def test_real_file_hash(video):
    assert sha256(video)==hashlib.sha256(video.read_bytes()).hexdigest()

def test_media_probe(video):
    m=get_video_metadata(video)
    assert m['duration_seconds']==2 and m['width']==64 and m['height']==64 and m['audio_present'] is False

def test_bad_media(tmp_path):
    p=tmp_path/'bad.mp4';p.write_text('not a video')
    with pytest.raises(ValueError):get_video_metadata(p)

def test_missing_media(tmp_path):
    with pytest.raises(ValueError):get_video_metadata(tmp_path/'missing.mp4')

def test_sample_limited():
    assert sample_seconds(300,1,3)==[0,1,2]

def test_sample_last_frame():
    assert sample_seconds(2,1,5)==[0,1,1.9]

def test_bad_sample_parameter():
    with pytest.raises(ValueError):sample_seconds(2,0,10)

def test_default_no_upload_and_no_invented_observations(video,tmp_path):
    e=intake(video,tmp_path/'out','internal QA','reference-only','restricted')
    assert e['source']['third_party_upload_allowed'] is False
    assert e['observations']==[] and e['hypotheses']==[]
    assert e['human_review']['status']=='not_reviewed'
    assert validate(e)

def test_actual_local_frames(video,tmp_path):
    e=intake(video,tmp_path/'out','internal QA','owned','internal',frames=True)
    assert len(e['sampling']['frames'])>=2
    assert all((tmp_path/'out'/f['path']).exists() for f in e['sampling']['frames'])
    assert all(len(f['sha256'])==64 for f in e['sampling']['frames'])

def test_timestamp_evidence_validation(video,tmp_path):
    e=intake(video,tmp_path/'out','owner','owned','public',frames=True)
    frame=e['sampling']['frames'][0]['path']
    e['observations'].append({'kind':'observed','claim':'visible red frame','time_seconds':0,'evidence_frames':[frame]})
    assert validate(e)
    e['observations'][0]['time_seconds']=100
    with pytest.raises(ValueError):validate(e)

def test_reject_unsourced_observation(video,tmp_path):
    e=intake(video,tmp_path/'out','owner','licensed','internal')
    e['observations'].append({'kind':'observed','claim':'object moved','time_seconds':1,'evidence_frames':['made_up.jpg']})
    with pytest.raises(ValueError):validate(e)

def test_reject_confident_hypothesis_disguised(video,tmp_path):
    e=intake(video,tmp_path/'out','owner','owned','restricted')
    e['hypotheses']=[{'kind':'observed','claim':'gravity caused the movement','limitations':'no measurements'}]
    with pytest.raises(ValueError):validate(e)

def test_unknown_privacy_rejected(video,tmp_path):
    with pytest.raises(ValueError):intake(video,tmp_path/'out','owner','owned','topsecret')

def test_empty_owner_rejected(video,tmp_path):
    with pytest.raises(ValueError):intake(video,tmp_path/'out',' ','owned','restricted')

def test_json_file_written(video,tmp_path):
    intake(video,tmp_path/'out','owner','owned','restricted')
    assert json.loads((tmp_path/'out'/'evidence.json').read_text())['schema']=='pryntor.video-evidence.v1'
