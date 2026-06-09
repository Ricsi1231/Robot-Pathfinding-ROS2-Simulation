"""Smoke tests for the bringup package skeleton.

Launch/config-only package, so these mirror Core's ``test_package.py`` style and
ensure the package imports and is well-formed.
"""

from __future__ import annotations

import robot_pathfinding_bringup


def test_package_is_importable() -> None:
    assert robot_pathfinding_bringup is not None


def test_version_is_non_empty_string() -> None:
    assert isinstance(robot_pathfinding_bringup.__version__, str)
    assert robot_pathfinding_bringup.__version__
