"""Command-line entry point for scenegen.

``scenegen`` is the installed console script (see pyproject.toml). Today
it is the launcher for the empty Isaac Lab scene; the validate / build /
preview subcommands arrive with T17.

Importing this module must not require Isaac Lab: ``scenegen --help`` and
``scenegen --version`` run on a clean machine with only the package
installed. The simulator is imported lazily, only when a scene is
actually launched.
"""

from __future__ import annotations

import argparse
import logging
import time

from scenegen import __version__
from scenegen.scene_config import build_simulation_cfg, max_steps, positive_float

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the ``scenegen`` argument parser.

    Isaac Lab's own launcher flags (--device, --headless, ...) are added
    when isaaclab is importable. Without it, --device is offered as a
    plain option so ``--help`` still works and parsing stays identical.
    """
    parser = argparse.ArgumentParser(
        prog="scenegen",
        description="Launch an empty Isaac Lab simulation.",
    )
    parser.add_argument("--version", action="version", version=f"scenegen {__version__}")
    try:
        from isaaclab.app import add_launcher_args
    except ImportError:
        parser.add_argument(
            "--device",
            default="cuda:0",
            help="Compute device (default cuda:0).",
        )
    else:
        add_launcher_args(parser)
    parser.add_argument(
        "--dt",
        type=positive_float,
        default=0.01,
        help="Simulation timestep in seconds (must be positive).",
    )
    parser.add_argument(
        "--duration",
        type=positive_float,
        default=None,
        metavar="SECONDS",
        help="Stop after this many simulated seconds (omit to run until stopped).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default INFO).",
    )
    return parser


def parse_args(argv=None) -> argparse.Namespace:
    """Parse launcher and simulation options.

    Parsing lives in a function (instead of at module import time) so the
    module can be imported without consuming ``sys.argv`` or exiting.
    """
    return build_parser().parse_args(argv)


def main(argv=None) -> None:
    """Launch Isaac Sim and step the empty scene until the app closes."""
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="[%(levelname)s] %(message)s")

    try:
        from isaaclab.app import launch_simulation

        import isaaclab.sim as sim_utils
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


if __name__ == "__main__":
    main()
