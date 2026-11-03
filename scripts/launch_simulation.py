"""Launch an empty Isaac Lab simulation and keep it running."""

import argparse
import logging
import time

from isaaclab.app import add_launcher_args, launch_simulation

try:
    from scene_config import build_simulation_cfg, max_steps, positive_float
except ImportError:  # running with the repo root on sys.path instead
    from scripts.scene_config import build_simulation_cfg, max_steps, positive_float


logger = logging.getLogger(__name__)

def parse_args(argv=None) -> argparse.Namespace:
    """Parse launcher and simulation options.

    Parsing lives in a function (instead of at module import time) so the
    module can be imported without consuming ``sys.argv`` or exiting.
    """
    parser = argparse.ArgumentParser(description="Start an empty Isaac Lab simulation.")
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
    return parser.parse_args(argv)

def main() -> None:
    """Launch Isaac Sim and step the empty scene until the app closes."""
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="[%(levelname)s] %(message)s")

    import isaaclab.sim as sim_utils

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
