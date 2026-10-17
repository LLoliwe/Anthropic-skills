import io, tempfile, unittest
from pathlib import Path
from zipfile import ZipFile
from install import SOURCES, extract, install

def mockzip(content):
 data=io.BytesIO()
 with ZipFile(data,"w") as archive:
  for name,body in content.items(): archive.writestr("root/"+name,body)
 return data.getvalue()

class Tests(unittest.TestCase):
 def test_good(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(extract(mockzip({"SKILL.md":"x","LICENSE":"MIT License"}),Path(d),""),2)
 def test_missing(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError): extract(mockzip({"README.md":"x"}),Path(d),"")
 def test_traversal(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError): extract(mockzip({"../../bad":"x","SKILL.md":"x"}),Path(d),"")
 def test_filter(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(extract(mockzip({"skills/baoyu-slide-deck/SKILL.md":"x","other/SKILL.md":"y"}),Path(d),"skills/baoyu-slide-deck/"),1)
 def test_install(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); archives=root/"archives"; archives.mkdir()
   for name in SOURCES:
    content={"skills/baoyu-slide-deck/SKILL.md":"x","LICENSE":"MIT License"} if name=="baoyu-slide-deck" else {"SKILL.md":"x","LICENSE":"MIT License"}
    (archives/(name+".zip")).write_bytes(mockzip(content))
   self.assertEqual(len(install(root/"installed",archives)),3)
   for slot in ("skills/_external",".agents/skills",".claude/skills"):
    for name in SOURCES:
     self.assertTrue((root/"installed"/slot/name/"SKILL.md").is_file())
     self.assertTrue((root/"installed"/slot/name/"LICENSE").is_file())

if __name__=="__main__":unittest.main()
