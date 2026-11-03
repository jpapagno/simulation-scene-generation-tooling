"""Stdlib unit tests for the scene_config helpers.

Run with: python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scene_config import max_steps, positive_float


class PositiveFloatTests(unittest.TestCase):
    def test_accepts_positive_values(self):
        self.assertEqual(positive_float("0.01"), 0.01)
        self.assertEqual(positive_float("5"), 5.0)

    def test_rejects_zero_and_negative(self):
        for bad in ("0", "-1", "-0.5"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                positive_float(bad)

    def test_rejects_non_finite(self):
        for bad in ("nan", "inf", "-inf"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                positive_float(bad)


class MaxStepsTests(unittest.TestCase):
    def test_none_duration_runs_forever(self):
        self.assertIsNone(max_steps(None, 0.01))

    def test_rounds_to_nearest_step(self):
        self.assertEqual(max_steps(5.0, 0.01), 500)
        self.assertEqual(max_steps(0.015, 0.01), 2)

    def test_at_least_one_step(self):
        self.assertEqual(max_steps(0.001, 0.01), 1)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            max_steps(float("nan"), 0.01)
        with self.assertRaises(ValueError):
            max_steps(5.0, 0.0)
        with self.assertRaises(ValueError):
            max_steps(-1.0, 0.01)


if __name__ == "__main__":
    unittest.main()
