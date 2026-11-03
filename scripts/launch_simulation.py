"""Launch an empty Isaac Lab simulation and keep it running."""

import argparse
import logging
import time

from isaaclab.app import add_launcher_args, launch_simulation

from scene_config import SceneConfig

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse launcher and scene arguments, validating scene values."""
    parser = argparse.ArgumentParser(description="Start an empty Isaac Lab simulation.")
    add_launcher_args(parser)
    parser.add_argument(
        "--dt",
        type=float,
        default=0.01,
        help="Simulation time step in seconds (must be positive).",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.0,
        help="Run for this many seconds, then exit. 0 runs until the app closes.",
    )
    args = parser.parse_args()
    if args.dt <= 0:
        parser.error("--dt must be positive.")
    if args.duration < 0:
        parser.error("--duration must be zero or positive.")
    return args


args = parse_args()
config = SceneConfig.from_args(args)

import isaaclab.sim as sim_utils


def main() -> None:
    """Launch Isaac Sim and step the empty scene until the app closes."""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    sim_cfg = config.build_simulation_cfg(sim_utils)

    with launch_simulation(sim_cfg, args):
        simulation = sim_utils.SimulationContext(sim_cfg)
        simulation.reset()
        logger.info("Empty simulation started. Close the window or press Ctrl+C to exit.")

        steps = 0
        start_time = time.monotonic()
        try:
            while simulation.is_running():
                if config.duration > 0 and steps * config.dt >= config.duration:
                    break
                simulation.step()
                steps += 1
        except KeyboardInterrupt:
            logger.info("Interrupted by user; shutting down.")
        finally:
            elapsed = time.monotonic() - start_time
            logger.info("Simulation stopped after %d steps (%.2f s).", steps, elapsed)


if __name__ == "__main__":
    main()
