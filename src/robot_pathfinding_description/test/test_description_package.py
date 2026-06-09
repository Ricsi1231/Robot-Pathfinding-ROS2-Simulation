"""Smoke tests for the description package skeleton.

Asset-only package, so there is no runtime logic to exercise; these mirror Core's
``test_package.py`` style and ensure the package imports and is well-formed.
"""

from __future__ import annotations

import robot_pathfinding_description


def test_package_is_importable() -> None:
    assert robot_pathfinding_description is not None


def test_version_is_non_empty_string() -> None:
    assert isinstance(robot_pathfinding_description.__version__, str)
    assert robot_pathfinding_description.__version__
