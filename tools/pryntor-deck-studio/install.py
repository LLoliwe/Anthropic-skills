#!/usr/bin/env python3
"""Install 3 commit-pinned MIT licensed agent skills without running vendor code."""
import argparse, io, json, shutil, stat, tempfile
from pathlib import Path, PurePosixPath
from urllib.request import urlopen
from zipfile import ZipFile

SOURCES = {
 "frontend-slides":("zarazhangrui","frontend-slides","9906a34d640d2111f724544cbc50f7f130569ae1",""),
 "baoyu-slide-deck":("JimLiu","baoyu-skills","1567581c26ec29f4216c6e6835415bf30343b0e3","skills/baoyu-slide-deck/"),
 "knowledge-cat-ppt-skill":("gnipbao","knowledge-cat-ppt-skill","889c3dc00b356607fa9af935eb807056c3394886",""),
}
MAX = 32 * 1024 * 1024

def extract(raw, target, prefix):
 count = total = 0
 with ZipFile(io.BytesIO(raw)) as archive:
  for entry in archive.infolist():
   if entry.is_dir(): continue
   parts = PurePosixPath(entry.filename).parts
   if len(parts) < 2: continue
   rel = PurePosixPath(*parts[1:])
   if prefix:
    if not str(rel).startswith(prefix): continue
    rel = PurePosixPath(str(rel)[len(prefix):])
   if not rel.parts or rel.is_absolute() or any(x in ("..",".") for x in rel.parts):
    raise ValueError("Unsafe archive path")
   if any(x in (".github",".git","node_modules","__pycache__",".venv") for x in rel.parts): continue
   if (entry.external_attr >> 16) & 0o170000 == stat.S_IFLNK:
    raise ValueError("Symlink in source archive")
   count += 1
   total += entry.file_size
   if count > 2500 or total > MAX or entry.file_size > 8 * 1024 * 1024:
    raise ValueError("Source archive size budget exceeded")
   path = target.joinpath(*rel.parts)
   path.parent.mkdir(parents=True,exist_ok=True)
   with archive.open(entry) as source, path.open("wb") as dest:
    shutil.copyfileobj(source,dest)
 if not count or not (target/"SKILL.md").is_file():
  raise ValueError("Missing SKILL.md")
 return count

def install(dest, archive_dir=None):
 dest = Path(dest).resolve()
 receipt=[]
 with tempfile.TemporaryDirectory() as d:
  temp=Path(d)
  for name,(owner,repo,sha,prefix) in SOURCES.items():
   url=f"https://codeload.github.com/{owner}/{repo}/zip/{sha}"
   if archive_dir:
    raw=(Path(archive_dir)/(name+".zip")).read_bytes()
   else:
    with urlopen(url,timeout=35) as response: raw=response.read(MAX+1)
   if len(raw)>MAX: raise ValueError("Compressed archive too large")
   out=temp/name
   out.mkdir()
   files=extract(raw,out,prefix)
   if name=="baoyu-slide-deck":
    with ZipFile(io.BytesIO(raw)) as archive:
     license_path=next((n for n in archive.namelist() if n.endswith("/LICENSE") and len(PurePosixPath(n).parts)==2),None)
     if not license_path: raise ValueError("Missing Baoyu upstream license")
     (out/"LICENSE").write_bytes(archive.read(license_path))
   if not (out/"LICENSE").is_file() or "MIT License" not in (out/"LICENSE").read_text(errors="replace")[:500]:
    raise ValueError("Missing or unrecognized upstream MIT license")
   receipt.append({"skill":name,"commit":sha,"files":files})
  # Only write project files after every upstream archive has passed checks.
  for rel in ("skills/_external",".agents/skills",".claude/skills"):
   parent=dest/rel
   parent.mkdir(parents=True,exist_ok=True)
   for name in SOURCES:
    target=parent/name
    if target.is_symlink(): raise ValueError("Refusing to overwrite symlink")
    with tempfile.TemporaryDirectory(prefix=".deck-stage-",dir=parent) as tmp:
     trial=Path(tmp)/name
     shutil.copytree(temp/name,trial)
     if target.exists(): shutil.rmtree(target)
     shutil.move(str(trial),str(target))
 return receipt

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--dest",default=".")
 p.add_argument("--archive-dir",default=None)
 a=p.parse_args()
 print(json.dumps({"installed":install(a.dest,a.archive_dir)},indent=2))
