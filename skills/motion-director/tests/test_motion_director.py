import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("motion_director", HERE / "scripts" / "motion_director.py")
md = importlib.util.module_from_spec(spec)
spec.loader.exec_module(md)
EXAMPLE = HERE / "examples" / "signal-demo.json"


class MotionDirectorTests(unittest.TestCase):
    def setUp(self):
        self.p = md.load(EXAMPLE)

    def test_demo_is_30_seconds(self):
        self.assertEqual(md.duration(self.p), 30)
        self.assertEqual(len(md.timeline(self.p)), 6)
        self.assertEqual(md.timeline(self.p)[-1]["end"], 30)

    def test_shot_boundary(self):
        self.assertEqual(md.shot_at(self.p, 0)[0]["id"], "S01")
        self.assertEqual(md.shot_at(self.p, 4)[0]["id"], "S02")
        self.assertEqual(md.shot_at(self.p, 9)[0]["id"], "S03")
        self.assertEqual(md.shot_at(self.p, 29.99)[0]["id"], "S06")

    def test_beat_grid(self):
        report = md.inspect(self.p)
        self.assertEqual(report["status"], "pass_with_warnings")
        self.assertFalse(report["errors"])
        self.assertTrue(all(m["beat_offset_seconds"] < 0.001 for m in report["measurements"]))

    def test_render_is_stateless_and_animated(self):
        a = md.seek(self.p, 2.0)
        b = md.seek(self.p, 2.0)
        c = md.seek(self.p, 3.5)
        self.assertEqual(a.size, (720, 720))
        self.assertEqual(a.tobytes(), b.tobytes())
        self.assertNotEqual(a.tobytes(), c.tobytes())

    def test_final_gate_requires_approval(self):
        self.assertEqual(len(md.inspect(self.p, require_approval=True)["errors"]), 6)
        with self.assertRaisesRegex(ValueError, "not approved"):
            md.render(self.p, Path("/tmp/should-not-exist.mp4"), 1, True, False)

    def test_revise_invalidates_approval(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "project.json"
            p = copy.deepcopy(self.p)
            md.approve(p, path, "S03", False)
            self.assertTrue(p["shots"][2]["approved"])
            md.revise(p, path, "S03", 4.5, "Focus the signal", "Cut tighter")
            self.assertFalse(p["shots"][2]["approved"])
            self.assertEqual(md.duration(md.load(path)), 29.5)
            self.assertEqual(len(p["history"]), 2)

    def test_handoff_creates_real_files(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            md.handoff(self.p, out)
            self.assertTrue((out/"contact_sheet.png").stat().st_size > 1000)
            self.assertTrue((out/"edit_decision_list.csv").stat().st_size > 100)
            self.assertFalse(json.loads((out/"provenance.json").read_text())["render_verified"])

    def test_duration_gate(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"project.json"
            p = copy.deepcopy(self.p)
            p["shots"][0]["duration"] = 62
            path.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError, "under 60"):
                md.load(path)



    def test_init_creates_new_editable_project(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "film.json"
            md.create_project(path, "Launch", "TEST", "Better choices", "designers", "social", "9:16", 120)
            p = md.load(path)
            self.assertEqual(p["height"], 1280)
            self.assertEqual(p["shots"][-1]["headline"], "BETTER CHOICES")
            self.assertEqual(md.duration(p), 30)

    def test_reorder_requires_complete_permutation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "film.json"
            p = copy.deepcopy(self.p)
            with self.assertRaisesRegex(ValueError, "exactly once"):
                md.reorder(p, path, "S02,S01")
            md.reorder(p, path, "S02,S01,S03,S04,S05,S06")
            self.assertEqual(md.load(path)["shots"][0]["id"], "S02")
            self.assertFalse(any(s["approved"] for s in p["shots"]))

    def test_missing_screenshot_blocks_render(self):
        p = copy.deepcopy(self.p)
        p["shots"][3]["asset"] = "/definitely/not/a/screenshot.png"
        self.assertTrue(any("does not exist" in e for e in md.inspect(p)["errors"]))


if __name__ == "__main__":
    unittest.main()
