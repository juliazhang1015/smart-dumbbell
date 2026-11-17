"""Checks for firmware/bringup/record_serial.py against a scripted serial port (simulation only).

No board is involved. A stand-in `serial` module replaces pyserial; the PORT argument selects
what the stand-in sends. Run from the repository root:

    python3 -m unittest tests.test_record_serial
"""
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

RECORDER = Path(__file__).resolve().parents[1] / "firmware" / "bringup" / "record_serial.py"

FAKE_SERIAL = r'''
import random, time

class Serial:
    """Sends 04_imu_stream-style rows; `port` names the fault to inject after 0.5 s."""
    def __init__(self, port, baud, timeout=1):
        self.s, self.timeout = port, timeout
        self.t0 = time.monotonic(); self.t_ms = 5000.0; self.done = False
        random.seed(1)
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def row(self, t=None, values=None):
        self.t_ms += 9.6
        v = values or ["%.3f" % random.gauss(m, 0.05) for m in (0.5, 0.1, 10.0, 0.1, -0.6, -0.3)]
        return ("%d,%s\n" % (int(self.t_ms) if t is None else t, ",".join(v))).encode()
    def silence(self):
        time.sleep(self.timeout); return b""
    def readline(self):
        late = time.monotonic() - self.t0 > 0.5
        s = self.s
        if s == "never": return self.silence()
        if s == "text":  time.sleep(0.01); return b"ERROR: LSM6DSOX not found at 0x6A. Run 03_i2c_scan.\n"
        if late and s == "silent": return self.silence()
        time.sleep(0.0096)
        if late and s == "frozen": return self.row(values=["0.000"] * 3 + ["0.00"] * 3)
        if late and not self.done:
            self.done = True
            if s == "jump":      self.t_ms += 1000
            if s == "backwards": self.t_ms = 100.0
            if s == "repeat":    self.t_ms -= 9.6; return self.row(t=int(self.t_ms + 9.6) - 9)
            if s == "nan":       return self.row(values=["nan", "0.100", "10.000", "0.10", "-0.60", "-0.30"])
            if s == "inf":       return self.row(values=["0.500", "0.100", "10.000", "inf", "-0.60", "-0.30"])
            if s == "negative":  return self.row(t=-5)
        return self.row()
'''


class TestRecorder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "fake").mkdir()
        (self.dir / "fake" / "serial.py").write_text(FAKE_SERIAL)
        self.out = self.dir / "P99_curl_slow_01.csv"
        self.env = dict(os.environ, PYTHONPATH=str(self.dir / "fake"))

    def tearDown(self):
        self.tmp.cleanup()

    def run_recorder(self, scenario, seconds="1.5", timeout=20):
        return subprocess.run([sys.executable, str(RECORDER), scenario, str(self.out), seconds],
                              env=self.env, capture_output=True, text=True, timeout=timeout)

    def assert_failed(self, scenario, message):
        t0 = time.monotonic()
        r = self.run_recorder(scenario)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn(message, r.stderr)
        self.assertFalse(self.out.exists(), "a failed take left a file under the final name")
        self.assertEqual(list(self.dir.glob("*.part")), [], "a failed take left a .part file")
        return time.monotonic() - t0

    def test_normal_take_is_saved(self):
        r = self.run_recorder("ok")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = self.out.read_text().splitlines()
        self.assertEqual(lines[0], "t_ms,ax,ay,az,gx,gy,gz")
        self.assertGreater(len(lines), 100)
        stamps = [float(l.split(",")[0]) for l in lines[1:]]
        self.assertTrue(all(b > a for a, b in zip(stamps, stamps[1:])))
        self.assertEqual(list(self.dir.glob("*.part")), [])

    def test_board_silent_after_start(self):
        took = self.assert_failed("silent", "no samples from the board")
        self.assertLess(took, 5, "the recorder waited too long on a silent board")

    def test_frozen_values(self):
        self.assert_failed("frozen", "frozen")

    def test_timestamp_jump(self):
        self.assert_failed("jump", "stalled")

    def test_timestamp_backwards(self):
        self.assert_failed("backwards", "repeated or backwards")

    def test_timestamp_repeated(self):
        self.assert_failed("repeat", "repeated or backwards")

    def test_negative_timestamp(self):
        self.assert_failed("negative", "negative timestamp")

    def test_nan_and_infinity(self):
        self.assert_failed("nan", "non-finite")
        self.assert_failed("inf", "non-finite")

    def test_nothing_ever_arrives(self):
        self.assert_failed("never", "no samples in 5 s")

    def test_only_text_arrives(self):
        self.assert_failed("text", "no samples in 5 s")

    def test_failed_take_keeps_an_earlier_good_file(self):
        self.out.write_text("t_ms,ax,ay,az,gx,gy,gz\n1,0,0,9.8,0,0,0\n")
        before = self.out.read_text()
        r = self.run_recorder("silent")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.out.read_text(), before)
        self.assertEqual(list(self.dir.glob("*.part")), [])

    @unittest.skipIf(os.name == "nt", "SIGINT delivery differs on Windows")
    def test_ctrl_c_keeps_what_was_recorded(self):
        p = subprocess.Popen([sys.executable, str(RECORDER), "ok", str(self.out), "30"],
                             env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(1.5)
        p.send_signal(signal.SIGINT)
        out, err = p.communicate(timeout=10)
        self.assertEqual(p.returncode, 0, err)
        self.assertIn("stopped by Ctrl-C", out)
        self.assertGreater(len(self.out.read_text().splitlines()), 50)
        self.assertEqual(list(self.dir.glob("*.part")), [])


if __name__ == "__main__":
    unittest.main()
