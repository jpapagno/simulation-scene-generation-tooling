"""Stdlib unit tests for the scenegen console-script entry point.

Run with: python -m unittest discover -s tests
(requires the package installed: pip install -e .)

The ``--help`` / ``--version`` checks run the entry point as a subprocess
so they prove the installed command works without Isaac Lab installed.
"""

import subprocess
import sys
import unittest

from scenegen import __version__
from scenegen.cli import parse_args


class ParseArgsTests(unittest.TestCase):
    def test_defaults(self):
        args = parse_args([])
        self.assertEqual(args.dt, 0.01)
        self.assertIsNone(args.duration)
        self.assertEqual(args.log_level, "INFO")
        self.assertEqual(args.device, "cuda:0")

    def test_options_parsed(self):
        args = parse_args(["--dt", "0.02", "--duration", "5", "--log-level", "DEBUG"])
        self.assertEqual(args.dt, 0.02)
        self.assertEqual(args.duration, 5.0)
        self.assertEqual(args.log_level, "DEBUG")

    def test_rejects_non_finite_dt(self):
        with self.assertRaises(SystemExit):
            parse_args(["--dt", "nan"])

    def test_rejects_bad_log_level(self):
        with self.assertRaises(SystemExit):
            parse_args(["--log-level", "VERBOSE"])


class EntryPointTests(unittest.TestCase):
    def test_help_exits_zero(self):
        proc = subprocess.run(
            [sys.executable, "-m", "scenegen", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("scenegen", proc.stdout)
        self.assertIn("--dt", proc.stdout)

    def test_version_reports_package_version(self):
        proc = subprocess.run(
            [sys.executable, "-m", "scenegen", "--version"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn(__version__, proc.stdout)

    def test_launch_without_isaaclab_fails_clearly(self):
        # No simulator is installed in the test environment: launching must
        # fail with a clear error and a non-zero exit, not a traceback from
        # an import at module load time.
        proc = subprocess.run(
            [sys.executable, "-m", "scenegen", "--duration", "0.01"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Isaac Lab is not installed", proc.stderr)


if __name__ == "__main__":
    unittest.main()
