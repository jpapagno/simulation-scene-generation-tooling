# Simulation Scene Generation Tooling

A minimal Isaac Lab starter project that launches an empty simulation scene and keeps it running. It is intended as a clean starting point for future scene-generation experiments.

## Requirements

- NVIDIA Isaac Sim and Isaac Lab installed and configured
- A supported NVIDIA GPU and driver for your Isaac Sim version

## Run

From the Isaac Lab repository root, copy this project into the repository or add its script to the Isaac Lab Python environment, then run:

```powershell
python scripts/launch_simulation.py
```

Alternatively, use the Isaac Lab launcher from its repository root:

```powershell
./isaaclab.bat -p path\to\simulation-scene-generation-tooling\scripts\launch_simulation.py
```

The script launches an empty `SimulationContext`, resets it, and steps until the simulator is closed. Launcher options such as `--device` are available; run the script with `--help` for the full list.

### Options

- `--dt SECONDS` — simulation timestep (must be positive, default `0.01`).
- `--duration SECONDS` — stop after this many simulated seconds instead of running until stopped. Useful for headless or scripted runs, e.g. `python scripts/launch_simulation.py --duration 5`.

Press Ctrl+C or close the simulator window to stop; the launcher shuts down gracefully and logs how many steps ran.

## Project layout

```text
scripts/
├── launch_simulation.py   # entry point: parses args, launches and steps the sim
└── scene_config.py        # tiny helpers: option validation and SimulationCfg builder
```

## References

- [Isaac Lab simulation launcher](https://isaac-sim.github.io/IsaacLab/main/source/how-to/launch_app.html)
- [Creating an empty scene](https://isaac-sim.github.io/IsaacLab/main/source/how-to/create_empty.html)
