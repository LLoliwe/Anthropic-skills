"""Fail-closed GenAI + Earshot 0.3 adapter tests. No external model calls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

FILE = Path(__file__).resolve().parents[1] / "scripts" / "earshot_genai_mix.py"
spec = importlib.util.spec_from_file_location("earshot_genai_mix", FILE)
mix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mix)


class ProofTests(unittest.TestCase):
    def test_digest_real_bytes_not_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.bin"
            p.write_bytes(b"our source")
            first = mix.digest(p)
            self.assertEqual(first, hashlib.sha256(b"our source").hexdigest())
            p.write_bytes(b"modified")
            self.assertNotEqual(first, mix.digest(p))

    def test_reject_incomplete_or_tampered_source(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "takes").mkdir()
            mp4 = d / "pryntor-motion-earshot-v03-preview.mp4"
            wav = d / "pryntor-motion-earshot-v03.wav"
            mp4.write_bytes(b"video-fixture")
            wav.write_bytes(b"audio-fixture")
            cues = [{"role": role} for role in ["tick", "snap", "whoosh.short", "click", "pop", "hit"]]
            good = {"earshot": "0.3.0", "bank": mix.BANK_VERSION,
                    "sample_rate": mix.RATE, "duration_s": 30.0,
                    "video_fps": 24, "cues": cues,
                    "preview_sha256": mix.digest(mp4), "wav_sha256": mix.digest(wav)}
            lock = {"earshot": "0.3.0", "bank": mix.BANK_VERSION, "sr": mix.RATE}
            (d / "soundtrack-evidence.json").write_text(json.dumps(good))
            (d / "takes" / "kit.lock.json").write_text(json.dumps(lock))
            self.assertEqual(mix.checked_source(d)[2], mp4)
            for change in [{"preview_sha256": "wrong"},
                           {"bank": "untrusted"}, {"sample_rate": 44100},
                           {"cues": cues[:5]}, {"duration_s": 33.0}]:
                with self.subTest(change=change):
                    (d / "soundtrack-evidence.json").write_text(json.dumps({**good, **change}))
                    with self.assertRaises(mix.BridgeError):
                        mix.checked_source(d)
            wav.write_bytes(b"tampered")
            (d / "soundtrack-evidence.json").write_text(json.dumps(good))
            with self.assertRaisesRegex(mix.BridgeError, "changed"):
                mix.checked_source(d)

    def test_model_provenance_must_be_supplied(self):
        # Static guard on the adapter's public CLI: consumers must name both
        # generator and immutable provider task, not silently imply a source.
        import argparse
        from unittest.mock import patch
        with patch("sys.argv", ["bridge", "--help"]):
            with self.assertRaises(SystemExit) as ctx:
                mix.main()
            self.assertEqual(ctx.exception.code, 0)

    def test_measured_onset_and_silent_rejection(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy installed only in audio-specific CI")
        signal = np.zeros((48000, 2), dtype=np.float64)
        signal[12000:16000] = 0.3
        ix, pk = mix.onset_samples(signal)
        self.assertEqual(ix, 12000)
        self.assertAlmostEqual(pk, 0.3)
        with self.assertRaises(mix.BridgeError):
            mix.onset_samples(np.zeros((48000, 2)))
        signal[14000, 0] = float("nan")
        with self.assertRaises(mix.BridgeError):
            mix.onset_samples(signal)


if __name__ == "__main__":
    unittest.main()
