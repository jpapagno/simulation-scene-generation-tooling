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

## Project layout

```text
scripts/
└── launch_simulation.py
```

## References

- [Isaac Lab simulation launcher](https://isaac-sim.github.io/IsaacLab/main/source/how-to/launch_app.html)
- [Creating an empty scene](https://isaac-sim.github.io/IsaacLab/main/source/how-to/create_empty.html)
