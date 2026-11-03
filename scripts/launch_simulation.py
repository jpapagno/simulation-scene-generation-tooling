"""Launch an empty Isaac Lab simulation and keep it running."""

import argparse

from isaaclab.app import add_launcher_args, launch_simulation


parser = argparse.ArgumentParser(description="Start an empty Isaac Lab simulation.")
add_launcher_args(parser)
args = parser.parse_args()

import isaaclab.sim as sim_utils


def main() -> None:
    """Launch Isaac Sim and step the empty scene until the app closes."""
    sim_cfg = sim_utils.SimulationCfg(device=args.device, dt=0.01)

    with launch_simulation(sim_cfg, args):
        simulation = sim_utils.SimulationContext(sim_cfg)
        simulation.reset()
        print("[INFO] Empty simulation started. Close the window or press Ctrl+C to exit.")

        while simulation.is_running():
            simulation.step()


if __name__ == "__main__":
    main()
