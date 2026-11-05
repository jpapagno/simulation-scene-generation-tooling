"""Stdlib unit tests for the backend layer (T03).

Run with: python -m unittest discover -s tests
(requires the package installed: pip install -e .)

T03 decouples the core from Isaac Lab: no module outside
``scenegen.backends`` may import a simulator, and importing the core —
or any backend module — must work with every simulator absent.
"""

import ast
import subprocess
import sys
import unittest
from pathlib import Path

import scenegen
from scenegen.backends import available_backends, get_backend
from scenegen.backends import isaaclab as isaaclab_backend

# Simulator top-level packages that must never appear in a core import.
SIMULATOR_MODULES = {"isaaclab", "isaacsim", "mujoco", "newton", "warp"}


class BackendRegistryTests(unittest.TestCase):
    def test_isaaclab_backend_is_available(self):
        self.assertIn("isaaclab", available_backends())

    def test_get_backend_returns_the_module(self):
        backend = get_backend("isaaclab")
        self.assertIs(backend, isaaclab_backend)
        self.assertEqual(backend.NAME, "isaaclab")
        for attr in ("add_launcher_args", "build_simulation_cfg", "launch"):
            self.assertTrue(callable(getattr(backend, attr)), attr)

    def test_get_backend_rejects_unknown_names(self):
        with self.assertRaises(ValueError):
            get_backend("not_a_backend")


class BackendImportsWithoutSimulatorTests(unittest.TestCase):
    def test_importing_backend_module_does_not_require_isaaclab(self):
        # The module imports cleanly here because isaaclab is not
        # installed in the test environment; its import is deferred to
        # the functions that use it.
        self.assertNotIn("isaaclab", sys.modules)

    def test_build_simulation_cfg_fails_clearly_without_isaaclab(self):
        with self.assertRaises(ImportError) as ctx:
            isaaclab_backend.build_simulation_cfg(device="cuda:0", dt=0.01)
        self.assertIn("Isaac Lab is not installed", str(ctx.exception))

    def test_whole_core_imports_without_any_simulator(self):
        # Fresh interpreter: import the core, the CLI and the backend
        # module, then prove no simulator module was pulled in.
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                "import scenegen.cli, scenegen.scene_config, "
                "scenegen.backends.isaaclab; import sys; "
                "assert not ({'isaaclab', 'isaacsim', 'mujoco', 'newton'} "
                "& set(sys.modules)), 'simulator module imported'",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)


class CoreNeverImportsSimulatorTests(unittest.TestCase):
    def test_no_core_module_imports_a_simulator(self):
        # Design rule 1: only modules under scenegen.backends may import
        # a simulator. Parse every core module's imports with ast so a
        # future simulator import fails loudly instead of creeping back.
        package_dir = Path(scenegen.__file__).resolve().parent
        offenders = []
        for path in sorted(package_dir.rglob("*.py")):
            if "backends" in path.relative_to(package_dir).parts:
                continue
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = {alias.name.split(".")[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom):
                    roots = {node.module.split(".")[0]} if node.module else set()
                else:
                    continue
                bad = roots & SIMULATOR_MODULES
                if bad:
                    offenders.append(f"{path.relative_to(package_dir)}: {sorted(bad)}")
        self.assertEqual(offenders, [])

    def test_scene_config_keeps_only_core_utilities(self):
        # T03: positive_float and max_steps stay in the core; the
        # SimulationCfg builder moved behind the backend layer.
        from scenegen import scene_config

        self.assertTrue(callable(scene_config.positive_float))
        self.assertTrue(callable(scene_config.max_steps))
        self.assertFalse(hasattr(scene_config, "build_simulation_cfg"))


if __name__ == "__main__":
    unittest.main()
