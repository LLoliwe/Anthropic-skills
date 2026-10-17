import ast
import pathlib
import unittest
p=pathlib.Path(__file__).with_name('red_hour_gallery.py')
src=p.read_text()

class LocalPreflight(unittest.TestCase):
    def test_parses(self):
        ast.parse(src)
    def test_no_credential_or_remote_inference(self):
        for s in ('requests.', 'urllib.', 'subprocess.', 'boto3','API_KEY','os.environ','api_key='):
            self.assertNotIn(s,src)
    def test_true_3d_and_export(self):
        for s in ('keyframe_insert', 'save_as_mainfile','CYCLES','render.render','frame_set'):
            self.assertIn(s,src)
    def test_artistic_approval_not_claimed(self):
        self.assertIn('PENDING — neither commercial release nor photorealism guaranteed',src)
    def test_render_budget_guard(self):
        self.assertIn('400 <= a.width <= 1440 and 8 <= a.samples <= 96',src)
    def test_source_originality(self):
        self.assertIn('third_party_models_or_textures',src)
        self.assertNotIn('download.blender.org',src)
if __name__=='__main__':unittest.main()
