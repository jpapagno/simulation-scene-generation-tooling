"""Simulator backends.

This package is the *only* place in the repo that may import a simulator.
Design rule 1 (ROADMAP.md): the core never imports a simulator — simulator
code lives behind the backend layer, so ``import scenegen`` and the core
test suite pass with every simulator absent.

Each backend module is imported lazily (see :func:`get_backend`) and must
not import its simulator at module level: the import happens inside the
functions that need it, so importing the backend module itself is always
safe. A backend that cannot find its simulator raises a clear error at
the point of use instead of failing at import time.
"""

from __future__ import annotations

import importlib

# Backends that exist in this package, in the order they are listed.
BACKENDS = ("isaaclab",)


def available_backends() -> list[str]:
    """Names of the backends shipped in this package."""
    return list(BACKENDS)


def get_backend(name: str):
    """Return the backend module for ``name``, importing it lazily.

    Raises:
        ValueError: if no backend with that name exists.
    """
    if name not in BACKENDS:
        raise ValueError(
            f"unknown backend {name!r}; available backends: {', '.join(BACKENDS)}"
        )
    return importlib.import_module(f"scenegen.backends.{name}")


__all__ = ["BACKENDS", "available_backends", "get_backend"]
