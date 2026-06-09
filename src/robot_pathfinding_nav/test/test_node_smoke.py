"""Smoke test for the pathfinding node.

Skipped automatically when rclpy is unavailable (e.g. running pytest outside a
sourced ROS 2 environment), so the pure-logic suite still runs everywhere.
"""

from __future__ import annotations

import pytest

rclpy = pytest.importorskip("rclpy")


def test_node_constructs_and_shuts_down() -> None:
    from robot_pathfinding_nav.pathfinding_node import PathfindingNode

    rclpy.init()
    try:
        node = PathfindingNode()
        assert node.get_name() == "pathfinding_node"
        node.destroy_node()
    finally:
        rclpy.shutdown()
