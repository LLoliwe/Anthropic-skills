import tempfile
import unittest
from pathlib import Path
from PIL import Image
from verify_motion import check

class MotionVerifierNegativeTests(unittest.TestCase):
    def images(self, root, animated):
        for i in range(1,50):
            im=Image.new('RGB',(400,225))
            pix=im.load()
            phase=i*.60 if animated else 0
            for y in range(225):
                for x in range(400):
                    pix[x,y]=(int((x+phase)*.5)%255,int((y+phase)*.8)%255,int((x+y+phase)*.35)%255)
            im.save(root/f'motion_{i:03}.png')
    def test_reject_static_slideshow(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.images(root,False)
            with self.assertRaises(AssertionError):check(root,400)
    def test_reject_missing_frame(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.images(root,True)
            (root/'motion_039.png').unlink()
            with self.assertRaises(AssertionError):check(root,400)

if __name__=='__main__':unittest.main()
