"""Command-line entry point for scenegen.

``scenegen`` is the installed console script (see pyproject.toml). Today
it is the launcher for the empty Isaac Lab scene; the validate / build /
preview subcommands arrive with T17.

This module is core code: it never imports a simulator. All
Isaac Lab-specific behaviour lives behind the backend layer
(``scenegen.backends.isaaclab``) and is reached lazily, so importing this
module and running ``scenegen --help`` / ``scenegen --version`` work on a
clean machine with only the package installed.
"""

from __future__ import annotations

import argparse
import logging

from scenegen import __version__
from scenegen.backends import get_backend
from scenegen.scene_config import positive_float

logger = logging.getLogger(__name__)

# The backend used by the launcher today. Other backends (MuJoCo, Newton,
# ...) arrive with their roadmap tasks; the CLI will select among them.
DEFAULT_BACKEND = "isaaclab"


def build_parser() -> argparse.ArgumentParser:
    """Build the ``scenegen`` argument parser.

    The backend contributes its launcher flags (--device, --headless, ...)
    when its simulator is importable; without it, --device is offered as
    a plain option so ``--help`` still works and parsing stays identical.
    """
    parser = argparse.ArgumentParser(
        prog="scenegen",
        description="Launch an empty Isaac Lab simulation.",
    )
    parser.add_argument("--version", action="version", version=f"scenegen {__version__}")
    get_backend(DEFAULT_BACKEND).add_launcher_args(parser)
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
    return parser


def parse_args(argv=None) -> argparse.Namespace:
    """Parse launcher and simulation options.

    Parsing lives in a function (instead of at module import time) so the
    module can be imported without consuming ``sys.argv`` or exiting.
    """
    return build_parser().parse_args(argv)


def main(argv=None) -> None:
    """Parse options and hand off to the backend to launch the scene."""
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="[%(levelname)s] %(message)s")
    get_backend(DEFAULT_BACKEND).launch(args)


if __name__ == "__main__":
    main()
