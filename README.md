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

- `--dt <seconds>`: simulation time step (default `0.01`, must be positive).
- `--duration <seconds>`: run for this long, then exit cleanly. `0` (the default) runs until the simulator is closed or Ctrl+C is pressed.

Scene settings are collected in `scripts/scene_config.py` (`SceneConfig`), so new options can be added there without touching the launcher.

## Project layout

```text
scripts/
├── launch_simulation.py
└── scene_config.py
```

## References

- [Isaac Lab simulation launcher](https://isaac-sim.github.io/IsaacLab/main/source/how-to/launch_app.html)
- [Creating an empty scene](https://isaac-sim.github.io/IsaacLab/main/source/how-to/create_empty.html)
