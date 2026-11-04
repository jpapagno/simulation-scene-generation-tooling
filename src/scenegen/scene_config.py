"""Small helpers for configuring the empty simulation scene.

Kept deliberately tiny: this module only validates the numeric options
the launcher accepts and builds the ``SimulationCfg`` for the empty
scene, so the launcher itself stays focused on running the simulation.
"""

from __future__ import annotations

import math


def positive_float(value: str) -> float:
    """Argparse type that accepts only strictly positive, finite floats."""
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"expected a positive, finite number, got {value!r}")
    return number


def build_simulation_cfg(device: str, dt: float):
    """Build the simulation config for an empty scene.

    The Isaac Lab import is deferred until this is called so importing
    this module never requires the simulator to be running.
    """
    from isaaclab.sim import SimulationCfg

    return SimulationCfg(device=device, dt=dt)


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
