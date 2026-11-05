"""Isaac Lab backend.

The only module in the tree that imports ``isaaclab``. Everything Isaac
Lab-specific lives here — the launcher flags, the ``SimulationCfg``
builder, and the launch-and-step loop — so the core package and the CLI
never touch the simulator.

Importing this module does *not* require Isaac Lab: the simulator is
imported inside the functions that use it. Calling any of them without
Isaac Lab installed raises an :class:`ImportError` (or, for
:func:`launch`, exits with a clear message) instead of failing at
import time.
"""

from __future__ import annotations

import argparse
import logging
import time

from scenegen.scene_config import max_steps

logger = logging.getLogger(__name__)

NAME = "isaaclab"


def _require_isaaclab():
    """Import Isaac Lab, or raise a clear error explaining it is missing."""
    try:
        import isaaclab.sim as sim_utils
        from isaaclab.app import launch_simulation
    except ImportError as exc:
        raise ImportError(
            "Isaac Lab is not installed in this Python environment. "
            "Install Isaac Sim / Isaac Lab and run scenegen from its Python "
            "environment to launch a simulation; `scenegen --help` works "
            "without it."
        ) from exc
    return launch_simulation, sim_utils


def add_launcher_args(parser: argparse.ArgumentParser) -> None:
    """Add Isaac Lab's launcher flags to ``parser``.

    When Isaac Lab is importable, its own flags (--device, --headless,
    ...) are added. Without it, --device is offered as a plain option so
    ``--help`` still works and parsing stays identical.
    """
    try:
        from isaaclab.app import add_launcher_args as _add_launcher_args
    except ImportError:
        parser.add_argument(
            "--device",
            default="cuda:0",
            help="Compute device (default cuda:0).",
        )
    else:
        _add_launcher_args(parser)


def build_simulation_cfg(device: str, dt: float):
    """Build the Isaac Lab simulation config for an empty scene.

    Raises:
        ImportError: if Isaac Lab is not installed.
    """
    _, sim_utils = _require_isaaclab()
    return sim_utils.SimulationCfg(device=device, dt=dt)


def launch(args: argparse.Namespace) -> None:
    """Launch Isaac Sim and step the empty scene until the app closes.

    ``args`` is the namespace produced by :func:`scenegen.cli.parse_args`.
    Exits with status 2 and a clear error message when Isaac Lab is not
    installed, instead of failing with a traceback.
    """
    try:
        launch_simulation, sim_utils = _require_isaaclab()
    except ImportError:
        logger.error(
            "Isaac Lab is not installed in this Python environment. "
            "Install Isaac Sim / Isaac Lab and run scenegen from its Python "
            "environment to launch a simulation; `scenegen --help` works without it."
        )
        raise SystemExit(2)

    sim_cfg = build_simulation_cfg(device=args.device, dt=args.dt)
    step_limit = max_steps(args.duration, args.dt)

    with launch_simulation(sim_cfg, args):
        simulation = sim_utils.SimulationContext(sim_cfg)
        simulation.reset()
        if step_limit is None:
            logger.info(
                "Empty simulation started (dt=%.4fs). Close the window or press Ctrl+C to exit.",
                args.dt,
            )
        else:
            logger.info(
                "Empty simulation started (dt=%.4fs, stopping after %.2fs / %d steps).",
                args.dt,
                args.duration,
                step_limit,
            )

        steps = 0
        started = time.monotonic()
        try:
            while simulation.is_running() and (step_limit is None or steps < step_limit):
                simulation.step()
                steps += 1
        except KeyboardInterrupt:
            logger.info("Interrupted by user; shutting down gracefully.")
        finally:
            elapsed = time.monotonic() - started
            logger.info(
                "Simulation stopped after %d steps (%.2fs wall time).", steps, elapsed
            )
