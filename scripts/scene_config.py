"""Small scene-configuration helper for the empty simulation launcher."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class SceneConfig:
    """Configuration for an empty simulation scene.

    ``duration`` is in seconds; 0 means run until the app closes.
    """

    device: str = "cuda:0"
    dt: float = 0.01
    duration: float = 0.0

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "SceneConfig":
        """Build a config from parsed launcher arguments."""
        return cls(
            device=getattr(args, "device", "cuda:0"),
            dt=args.dt,
            duration=args.duration,
        )

    def build_simulation_cfg(self, sim_utils):
        """Build an Isaac Lab ``SimulationCfg`` for this scene."""
        return sim_utils.SimulationCfg(device=self.device, dt=self.dt)
