# Simulation Scene Generation Tooling

A simulator-agnostic tool for scene generation, synthetic data generation,
and domain randomization: one user-defined YAML file in, the same scene out
for Isaac Sim, Isaac Lab, MuJoCo, Newton, and other simulators. See
[ROADMAP.md](ROADMAP.md) for the plan (T01–T35).

Today the repo is a minimal Isaac Lab starter that launches an empty
simulation scene and keeps it running. It is intended as a clean starting
point for future scene-generation experiments.

## Install

The core package is stdlib-only and installs without any simulator:

```powershell
pip install -e .
```

That installs the `scenegen` command. Check it works:

```powershell
scenegen --help
scenegen --version
```

## Requirements (to actually launch a scene)

- NVIDIA Isaac Sim and Isaac Lab installed and configured
- A supported NVIDIA GPU and driver for your Isaac Sim version

`scenegen --help` works without Isaac Lab; launching a simulation does not.

## Run

From the Isaac Lab Python environment, run:

```powershell
scenegen
```

Alternatively, use the Isaac Lab launcher from its repository root:

```powershell
./isaaclab.bat -p path\to\simulation-scene-generation-tooling\scripts\launch_simulation.py
```

The launcher starts an empty `SimulationContext`, resets it, and steps
until the simulator is closed. Launcher options such as `--device` are
available when Isaac Lab is installed; run `scenegen --help` for the full
list.

### Options

- `--dt SECONDS` — simulation timestep (must be positive and finite, default `0.01`).
- `--duration SECONDS` — stop after this many simulated seconds instead of running until stopped. Useful for headless or scripted runs, e.g. `scenegen --duration 5`.
- `--log-level LEVEL` — logging verbosity: `DEBUG`, `INFO`, `WARNING`, or `ERROR` (default `INFO`).

Press Ctrl+C or close the simulator window to stop; the launcher shuts down gracefully and logs how many steps ran.

## Tests

The test suite is stdlib-only (no extra dependencies). Install the package
first, then run:

```powershell
pip install -e .
python -m unittest discover -s tests
```

## Project layout

```text
pyproject.toml            # packaging: src layout, scenegen console script
src/scenegen/
├── __init__.py           # package version
├── __main__.py           # `python -m scenegen`
├── cli.py                # entry point: parses args, launches and steps the sim
└── scene_config.py       # tiny helpers: option validation and SimulationCfg builder
scripts/
└── launch_simulation.py  # thin shim for the Isaac Lab `-p <script>` workflow
tests/
├── test_cli.py           # tests for the scenegen entry point
└── test_scene_config.py  # tests for the scene_config helpers
```

## References

- [Isaac Lab simulation launcher](https://isaac-sim.github.io/IsaacLab/main/source/how-to/launch_app.html)
- [Creating an empty scene](https://isaac-sim.github.io/IsaacLab/main/source/how-to/create_empty.html)
