"""Pryntor Earshot 0.3 sound-kit regressions; no model or external API required."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "earshot_v03_soundtrack.py"
spec = importlib.util.spec_from_file_location("earshot_v03_soundtrack", SCRIPT)
soundtrack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(soundtrack)
FILM = Path(__file__).resolve().parents[1] / "examples" / "signal-demo.json"


class SoundtrackTests(unittest.TestCase):
    def test_exact_existing_30_second_six_shot_frame_plan(self):
        plan = soundtrack.build_plan(json.loads(FILM.read_text()))
        self.assertEqual(plan["fps"], 24)
        self.assertEqual(plan["frames"], 720)
        self.assertEqual(plan["duration_s"], 30)
        self.assertEqual([(x["shot"], x["role"], x["frame"]) for x in plan["cues"]], [
            ("S01", "tick", 48), ("S02", "snap", 156),
            ("S03", "whoosh.short", 276), ("S04", "click", 408),
            ("S05", "pop", 540), ("S06", "hit", 660)])

    def test_reject_bad_shots_and_fractional_frames(self):
        valid = {"fps": 24, "shots": [{"id": "A", "type": "hook", "duration": 4}]}
        changes = [
            {"fps": 0}, {"fps": 29.97},
            {"shots": [{"id": "A", "type": "unknown", "duration": 4}]},
            {"shots": [{"id": "A", "type": "hook", "duration": 4.011}]},
            {"shots": [{"id": "A", "type": "hook", "duration": 4},
                       {"id": "A", "type": "cta", "duration": 2}]},
            {"shots": [{"id": "A", "type": "hook", "duration": 0.02}]}
        ]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(soundtrack.SoundtrackError):
                soundtrack.build_plan({**valid, **change})

    def fixture(self, temp, role="tick"):
        outdir = Path(temp)
        name = role.replace(".", "-") + "_1.wav"
        p = outdir / name
        p.write_bytes(b"original test bytes")
        spec = soundtrack.SOUND_KIT["roles"][role]
        alignment = spec["align"]
        t = {"file": name, "sha1": hashlib.sha1(p.read_bytes()).hexdigest(),
             "onset_s": 0.0, "peak_s": 0.01, "end_s": 0.1,
             "dur_s": 0.11, "checks": [], "seed": 1}
        lock = {"kit": 1, "earshot": "0.3.0",
                "bank": soundtrack.BANK_VERSION, "sr": 48000,
                "roles": {role: {"sound": spec["sound"], "align": alignment,
                                 "level_db": -8.0, "takes": [t]}}}
        return lock, p

    def test_lock_requires_exact_audited_untampered_take(self):
        with tempfile.TemporaryDirectory() as d:
            lock, src = self.fixture(d)
            self.assertEqual(soundtrack.checked_take(lock, "tick", Path(d))[0], src)
            src.write_bytes(b"changed bytes")
            with self.assertRaisesRegex(soundtrack.SoundtrackError, "checksum"):
                soundtrack.checked_take(lock, "tick", Path(d))

    def test_reject_bad_version_bank_audit_and_unsafe_path(self):
        with tempfile.TemporaryDirectory() as d:
            lock, _ = self.fixture(d)
            alterations = [
                lambda x: x.update(earshot="0.2.0"),
                lambda x: x.update(bank="unverified"),
                lambda x: x["roles"]["tick"]["takes"][0].update(checks=["clipping"]),
                lambda x: x["roles"]["tick"]["takes"][0].update(file="../escape.wav"),
                lambda x: x["roles"]["tick"].update(align="peak"),
            ]
            for change in alterations:
                data = json.loads(json.dumps(lock))
                change(data)
                with self.subTest(change=str(change)), self.assertRaises(soundtrack.SoundtrackError):
                    soundtrack.checked_take(data, "tick", Path(d))

    def test_actual_sample_exact_wav_mix(self):
        try:
            import numpy as np
            import soundfile as sf
        except ImportError:
            self.skipTest("NumPy/soundfile installed only in Earshot audio CI")
        with tempfile.TemporaryDirectory() as d:
            lock, src = self.fixture(d)
            y = np.sin(2 * np.pi * 320 * np.arange(4800) / 48000).astype("float32") * 0.22
            sf.write(src, y, 48000, subtype="PCM_24")
            lock["roles"]["tick"]["takes"][0]["sha1"] = hashlib.sha1(src.read_bytes()).hexdigest()
            film = {"fps": 24, "shots": [{"id": "S01", "type": "hook", "duration": 4}]}
            plan = soundtrack.build_plan(film)
            result_path = Path(d) / "mix.wav"
            result = soundtrack.mix(plan, lock, Path(d), result_path)
            self.assertEqual(result["status"], "rendered_technical_only")
            self.assertEqual(len(result["cues"]), 1)
            result_y, sr = sf.read(result_path, always_2d=True)
            self.assertEqual(sr, 48000)
            self.assertEqual(len(result_y), 192000)
            self.assertTrue(np.all(result_y[:95999] == 0))
            self.assertGreater(float(np.max(np.abs(result_y[96000:100000]))), 0.01)
            self.assertFalse(result["human_audio_and_film_approval"])


if __name__ == "__main__":
    unittest.main()
