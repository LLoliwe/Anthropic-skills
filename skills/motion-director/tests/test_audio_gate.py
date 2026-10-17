"""True ffprobe/ffmpeg integration checks with generated, original test fixtures."""
import importlib.util
import math
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import wave

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audio_gate.py"
spec = importlib.util.spec_from_file_location("audio_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def wav(path, amplitude=0.25, silence=False):
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        out = [0 if silence else round(32767 * amplitude * math.sin(2*math.pi*440*t/16000))
               for t in range(16000)]
        f.writeframes(struct.pack("<"+"h"*len(out), *out))


class AudioGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_real_audio_passes_technical_gate(self):
        p = self.root / "test.wav"; wav(p)
        result = gate.inspect_audio(p)
        self.assertEqual(result["status"], "pass_technical_only")
        self.assertEqual(result["audio_streams"], 1)
        self.assertLess(result["max_sample_peak_dbfs"], -0.5)

    def test_silent_audio_fails(self):
        p = self.root / "silence.wav"; wav(p, silence=True)
        result = gate.inspect_audio(p)
        self.assertIn("audio_too_quiet", result["failures"])

    def test_silence_exception_still_needs_director(self):
        p = self.root / "intent.wav"; wav(p, silence=True)
        result = gate.inspect_audio(p, intentional_mute="intended for silent lobby display")
        self.assertEqual(result["status"], "pass_with_warnings")
        self.assertIn("director_must_approve", result["warnings"][0])

    def test_peak_fails(self):
        p = self.root / "hot.wav"; wav(p, amplitude=0.99)
        self.assertIn("sample_peak_exceeds_limit", gate.inspect_audio(p)["failures"])

    def test_missing_file_fails_closed(self):
        with self.assertRaises(ValueError):
            gate.inspect_audio(self.root / "absent.mp4")

    def test_video_with_no_audio_fails(self):
        p = self.root / "mute.mp4"
        proc = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                               "color=c=black:s=64x64:r=4", "-t", "1", "-c:v", "mpeg4", str(p)],
                              capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        self.assertIn("audio_stream_missing", gate.inspect_audio(p)["failures"])

    def test_unavailable_earshot_honestly_blocked(self):
        # No model inference can be asserted from a technical validation test.
        self.assertIn(gate.earshot_review(self.root / "no.mp4")["status"], ("blocked",))

    def test_cli_outputs_evidence(self):
        p = self.root / "test.wav"; out = self.root / "qa.json"; wav(p)
        result = subprocess.run([sys.executable, str(SCRIPT), str(p), "--report", str(out)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(out.is_file())
        self.assertIn("pass_technical_only", out.read_text())


if __name__ == "__main__":
    unittest.main()
