"""Core helpers for configuring a simulation run.

This module is core code: it is stdlib-only and never imports a simulator
(see ROADMAP.md design rule 1). It keeps the small pure utilities the
launcher needs — validating numeric options and turning a duration into a
step count. Anything simulator-specific lives behind the backend layer
(``scenegen.backends``); the Isaac Lab ``SimulationCfg`` builder moved to
``scenegen.backends.isaaclab`` with T03.
"""

from __future__ import annotations

import math


def positive_float(value: str) -> float:
    """Argparse type that accepts only strictly positive, finite floats."""
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"expected a positive, finite number, got {value!r}")
    return number


def max_steps(duration: float | None, dt: float) -> int | None:
    """Number of steps needed to run for ``duration`` seconds.

    Returns ``None`` when no duration was given (run until stopped).
    """
    if duration is None:
        return None
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"expected a positive, finite duration, got {duration!r}")
    if not math.isfinite(dt) or dt <= 0:
        raise ValueError(f"expected a positive, finite timestep, got {dt!r}")
    return max(1, int(round(duration / dt)))
