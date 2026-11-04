# Roadmap: Simulation Scene Generation Tooling

A simulator-agnostic tool for scene generation, synthetic data generation, and
domain randomization.

## Vision

One user-defined YAML file in, the same scene out for any simulator:

- **Input:** a YAML file written by the user describing a scene.
- **Output:** a scene for Isaac Sim, Isaac Lab, MuJoCo, Newton, and other
  simulators — the same scene, semantically, on every backend.
- **On top:** synthetic data generation (RGB, depth, segmentation, bounding
  boxes, object poses) and domain randomization (pose, scale, colour/material,
  lighting, physics, clutter) driven from the same YAML.

The north star is a single YAML file that produces a working, labelled,
randomizable scene everywhere. The roadmap is not done until the final
golden-scene test (T35) passes for every backend.

## Current state

As of 2026-11-04 the repo is packaged as `scenegen` (T01 done) with no
import path tricks left (T02 done): `pip install -e .` installs the
`scenegen` console script, the core is stdlib-only and imports without
Isaac Lab installed from any working directory, and the launcher lives
in `src/scenegen/cli.py` with `scripts/launch_simulation.py` kept as a
thin shim for the Isaac Lab `-p` workflow. A regression test imports
`scenegen` from an unrelated directory. There is no YAML input, no
scene model, no backend other than Isaac Lab, no assets, no
randomization, and no data capture yet.

## Architecture

```
User YAML  ->  validated Scene IR  ->  per-simulator backends
                                         |- Isaac Sim (USD)
                                         |- Isaac Lab (scene config)
                                         |- MuJoCo (MJCF)
                                         |- Newton (USD)
                                         '- ...others
```

- **YAML** is the only thing the user writes. It is versioned (schema v1).
- **Scene IR** is a typed, validated, simulator-neutral model of a scene:
  scene, objects, lights, cameras, physics, materials. Every conversion
  between representations happens in exactly one place.
- **Backends** translate the IR into a simulator's native format. A backend
  never feeds back into the IR.

## Design rules

1. The core never imports a simulator. Simulator code lives behind the
   backend layer only, so `import scenegen` and the core test suite pass with
   `isaaclab` (and every other simulator) absent.
2. Units and coordinates are fixed once, in the IR: metres, kilograms,
   degrees for user-facing angles, **Z-up**, quaternions in **wxyz** order.
   Each backend converts at its edge.
3. Randomization resolves before the backend runs: one YAML + seed expands
   into concrete IR scenes, and the backend only ever sees a concrete scene.
4. Unsupported features **warn, never silently drop**. A backend that cannot
   do something says so by name, in the build output and in the manifest.
5. USD is an output, not the model. The IR is the source of truth; USD,
   MJCF, and Isaac Lab scene configs are generated from it.
6. Determinism is a feature: the same YAML + seed produces byte-identical
   output; a different seed produces a different, still valid scene.

## YAML schema v1 — example

```yaml
schema_version: 1
name: tabletop
metadata:
  description: Ground plane, table, cube, light, camera

environment:
  gravity: [0, 0, -9.81]

physics:
  dt: 0.01

objects:
  - name: ground
    type: plane
    static: true
    size: [10, 10]
  - name: table
    type: box
    static: true
    size: [1.2, 0.8, 0.05]
    position: [0, 0, 0.4]
    material:
      color: [0.55, 0.45, 0.35]
  - name: cube
    type: box
    size: [0.1, 0.1, 0.1]
    position: [0.2, 0.1, 0.5]
    mass: 0.5
    friction: 0.8
    material:
      color: [0.8, 0.2, 0.2]

lights:
  - name: sun
    type: directional
    direction: [0.5, -0.5, -1.0]
    intensity: 1.0

cameras:
  - name: main
    position: [1.2, -1.2, 1.0]
    look_at: [0, 0, 0.4]
    resolution: [640, 480]

randomization: {}
outputs:
  rgb: true
  depth: true
```

## Milestones

### M0 — Foundation (T01–T04)

Package the project, remove import-path tricks, decouple the core from Isaac
Lab, and add CI and quality gates. After M0 the tool is a real installable
package with a test suite that runs without any simulator installed.

### M1 — First scene (T05–T09)

YAML loader with readable errors, schema v1, the Scene IR, the first backend
(USD for Isaac Sim), and examples with golden tests. After M1 one YAML file
produces one real scene end-to-end.

### M2 — Usable core (T10–T14, T17–T18)

Primitives and environment library, transforms done once correctly, physics
and materials in the IR, Isaac Lab and MuJoCo backends, plus the CLI and
deterministic seeding. After M2 the same YAML builds for three simulators.

### M3 — Newton + parity (T15–T16)

Newton backend — a time-boxed spike first, then the build — and backend
conformance tests that assert every backend output contains the same objects,
poses, and physics within tolerance. After M3 four backends agree on the same
scene, or the disagreement is a named, tracked blocker.

### M4 — Randomization + data (T19–T25)

Randomization syntax in YAML, sampler engine, presets, cameras and sensors,
synthetic data capture specification, dataset manifest and reproducibility,
batch and headless generation. After M4 a YAML file expands into a labelled,
reproducible dataset.

### M5 — Polish + release (T26–T34)

USD interchange depth, external asset import, composition, scene
diagnostics, preview and summary, documentation that teaches, schema
versioning and migration, a performance pass, and the first versioned release.
After M5 the tool is usable by someone other than its author.

### M6 — Proven (T35)

The golden-scene end-to-end acceptance test. The roadmap is only done when
T35 passes for Isaac Sim, Isaac Lab, MuJoCo, and Newton from a clean checkout.

## Backend capability matrix

Backends will never be feature-identical. The matrix below is the target to
fill in as backends land; a cell is either supported, supported with a named
limitation, or explicitly unsupported (with a warning at build time).

| Capability | Isaac Sim (USD) | Isaac Lab | MuJoCo (MJCF) | Newton |
|---|---|---|---|---|
| Primitives (box, sphere, cylinder, capsule, plane) | target | target | target | target |
| Lights (directional, point, dome) | target | target | target | target |
| Cameras (RGB, depth, segmentation) | target | target | target | target |
| Rigid bodies, mass, friction, restitution | target | target | target | target |
| Static bodies | target | target | target | target |
| Materials (colour, roughness) | target | target | target | target |
| External assets (USD, URDF, MJCF, OBJ, glTF) | varies | varies | varies | varies |
| Headless stepping | target | target | target | target |

Where a backend cannot do something, it warns by name and records the
warning in the manifest — it never silently drops the feature.

## Decisions and risks

- **USD as an output, IR as the model:** keeps one input working across
  simulators instead of letting USD become a second, divergent model.
- **Newton needs a spike (T15):** its API is newer than the others, so the
  backend starts time-boxed and the spike findings decide the build — or a
  blocker becomes its own task.
- **Backends will never be feature-identical:** the conformance tests (T16)
  and the warning rule exist so drift is caught and named, not hidden.

## Task list

Work proceeds in dependency order. Pick the next highest-priority open task
that is not already done; if a task is too big for one run, do the next
coherent slice and note the remainder. If a run finds a bug, a gap, or a
task that is wrong, too big, blocked, or out of order, update this file and
the matching GitHub Issue instead of silently dropping the finding.

| Task | Title | Priority | Size | Depends on | Done when |
|---|---|---|---|---|---|
| T01 | Package the project | P0 | M | — | `pip install -e .` works on a clean machine and `scenegen --help` runs |
| T02 | Remove import path tricks | P0 | S | T01 | No `sys.path` edits remain; imports work from any working directory |
| T03 | Decouple the core from Isaac Lab | P0 | M | T01 | `import scenegen` and the full core test suite pass with `isaaclab` absent |
| T04 | Add CI and basic quality gates | P0 | S | T01, T03 | GitHub Actions green on main; a failing test blocks merge visually |
| T05 | YAML loader with readable errors | P0 | M | T01 | Each malformed fixture produces an expected one-line error and non-zero exit, no traceback |
| T06 | Define schema v1 | P0 | L | T05 | The example above validates; each documented invalid case fails with the field named |
| T07 | Define the Scene IR | P0 | L | T06 | Loaded YAML round-trips to an IR instance and back to an equivalent dictionary in tests |
| T08 | First backend: USD for Isaac Sim | P0 | L | T07 | Building the example writes a USD file that opens in Isaac Sim / a USD viewer with the expected objects at the expected poses |
| T09 | Examples and golden tests | P0 | M | T08 | Both examples build in CI; a deliberate change to a golden file is the only way output changes |
| T10 | Primitives and environment library | P1 | M | T07 | Every primitive and light type appears correctly in USD output and tests |
| T11 | Transforms done once, correctly | P1 | M | T07 | Rotation tests cover 90-degree cases on each axis and quaternion/Euler equivalence |
| T12 | Physics and materials in the IR | P1 | M | T07 | Invalid combinations (mass on a static body) are validation errors |
| T13 | Isaac Lab backend | P1 | L | T10–T12 | The tabletop example launches in Isaac Lab from generated output |
| T14 | MuJoCo backend | P1 | L | T10–T12 | The same example loads in MuJoCo (`mujoco.MjModel.from_xml_path`) and steps without error |
| T15 | Newton backend — spike, then build | P1 | XL | T10–T12 | Spike notes in the repo; the example builds and steps in Newton, or the blocker becomes a new task |
| T16 | Backend conformance tests | P1 | M | T13–T15 | The suite runs for all four backend outputs; translation drift fails it |
| T17 | Command-line experience | P1 | M | T08 | All three subcommands match the README; errors go to stderr with a non-zero exit |
| T18 | Deterministic seeding | P1 | M | T07 | Two builds with the same seed produce byte-identical scene files; different seeds differ |
| T19 | Randomization syntax in YAML | P2 | L | T06, T18 | The schema accepts and validates each distribution form; bad ranges fail with the field named |
| T20 | Sampler engine | P2 | L | T19 | `--variants 20 --seed 42` yields 20 distinct scenes; re-running yields the identical 20 |
| T21 | Domain randomization presets | P2 | M | T20 | Each preset has an example file and a test showing only its intended fields vary |
| T22 | Cameras and sensors completed | P2 | M | T07, T19 | A camera in YAML appears in every backend that supports it, and warns by name where it does not |
| T23 | Synthetic data capture specification | P2 | L | T22 | The capture spec is documented and validated; one backend produces a sample capture matching it |
| T24 | Dataset manifest and reproducibility | P2 | M | T20 | Given only the manifest, a user can regenerate the identical batch |
| T25 | Batch and headless generation | P2 | M | T20, T24 | A 100-variant batch completes headlessly; one bad variant fails alone and is named in the summary |
| T26 | USD interchange depth | P3 | L | T08 | A scene with 100 repeated objects uses instancing and opens correctly in Isaac Sim |
| T27 | External asset import | P3 | L | T07 | Each format has one working example or one explicit unsupported warning per backend |
| T28 | Composition | P3 | M | T06 | Two examples share one fragment; changing the fragment changes both builds |
| T29 | Scene diagnostics | P3 | M | T16 | Each diagnostic has a fixture that triggers it and a clear message naming the object |
| T30 | Preview and scene summary | P3 | M | T08 | A summary prints for every backend; the scene can be sanity-checked without opening a simulator |
| T31 | Documentation that teaches | P3 | M | T17 | A new user reaches a generated scene from the quickstart alone; the schema reference cannot drift from the code |
| T32 | Schema versioning and migration | P3 | M | T06 | A v1 file still builds, or fails with migration instructions, after any future v2 exists |
| T33 | Performance pass | P3 | M | T26 | A 1,000-object scene builds in seconds, with a recorded benchmark in the repo |
| T34 | First versioned release | P3 | S | T31 | A release exists, installs from the tag, and all examples build in CI |
| T35 | Golden-scene end-to-end acceptance test | Final | L | T13–T16, T20, T23–T24 | Every acceptance criterion below passes for Isaac Sim, Isaac Lab, MuJoCo, and Newton, from a clean checkout, with the report checked into the repo |

## T35 — Golden-scene end-to-end acceptance test (definition of done)

One fixed YAML scene, `examples/golden.yaml` — ground plane; static table;
three rigid objects (box, sphere, cylinder) with named poses, masses,
friction, and colours; one directional light; one camera at a fixed
resolution — is generated for every backend. Then:

1. It generates with a manifest and no unexplained warnings.
2. It loads in its native format: USD opens, MJCF compiles, Newton loads.
3. It is the same scene semantically, within 1 mm / 0.5 degrees, on every
   backend.
4. It steps headlessly for 100 steps with no exception or NaN; objects
   settle, they do not fall through.
5. Capture produces RGB, depth, segmentation, and bounding boxes for the
   three objects, matching their names.
6. Randomization is reproducible: the same seed gives an identical scene;
   different seeds give different poses/lighting within the declared ranges
   with the same object inventory.

This is the definition of done for the whole roadmap. A partial pass is a
fail.
