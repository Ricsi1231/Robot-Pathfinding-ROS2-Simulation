"""Pure-logic seam between ROS occupancy grids and Robot-Pathfinding-Core.

This module is intentionally **free of any ROS imports** so it can be unit-tested
and ``mypy``-checked without a ROS 2 environment. It depends only on the Core
library (``robot_pathfinding``) and the standard library. The ROS node
(``pathfinding_node``) is responsible for extracting the plain values below from
``nav_msgs/OccupancyGrid`` / ``geometry_msgs`` messages and feeding them here.

Coordinate conventions follow ``nav_msgs/OccupancyGrid``:

* ``data`` is row-major, length ``width * height``; index ``y * width + x``.
* Each cell holds an occupancy probability ``0..100``, or ``-1`` for unknown.
* The grid origin (cell ``(0, 0)`` corner) sits at world ``(origin_x, origin_y)``
  and each cell spans ``resolution`` metres.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from robot_pathfinding import Grid, PathResult, Point

# OccupancyGrid sentinel for an unobserved cell.
UNKNOWN: int = -1


@dataclass(frozen=True, slots=True)
class GridMetadata:
    """The pose/scale half of a ``nav_msgs/OccupancyGrid`` (``info`` field).

    Captures everything needed to convert between integer grid cells and
    continuous world coordinates, without depending on ROS message types.
    """

    width: int
    height: int
    resolution: float
    origin_x: float = 0.0
    origin_y: float = 0.0


def occupancy_to_grid(
    data: Sequence[int],
    metadata: GridMetadata,
    *,
    occupied_threshold: int = 50,
    unknown_is_obstacle: bool = True,
    allow_diagonal: bool = True,
) -> Grid:
    """Build a Core :class:`Grid` from a flat occupancy buffer.

    A cell becomes an obstacle when its value is ``>= occupied_threshold``, or
    when it is :data:`UNKNOWN` and ``unknown_is_obstacle`` is set (the safe
    default for navigation: treat unobserved space as blocked).

    Raises:
        ValueError: if ``data`` length does not match ``width * height``.
    """
    expected = metadata.width * metadata.height
    if len(data) != expected:
        raise ValueError(
            f"occupancy data length {len(data)} != width*height {expected}"
        )

    obstacles: list[Point] = []
    for index, value in enumerate(data):
        is_obstacle = value >= occupied_threshold or (
            value == UNKNOWN and unknown_is_obstacle
        )
        if is_obstacle:
            y, x = divmod(index, metadata.width)
            obstacles.append(Point(x, y))

    return Grid(
        metadata.width,
        metadata.height,
        obstacles,
        allow_diagonal=allow_diagonal,
    )


def world_to_cell(x: float, y: float, metadata: GridMetadata) -> Point:
    """Convert continuous world coordinates to an integer grid cell."""
    cell_x = int((x - metadata.origin_x) / metadata.resolution)
    cell_y = int((y - metadata.origin_y) / metadata.resolution)
    return Point(cell_x, cell_y)


def cell_to_world(point: Point, metadata: GridMetadata) -> tuple[float, float]:
    """Convert a grid cell to the world coordinates of its centre."""
    world_x = metadata.origin_x + (point.x + 0.5) * metadata.resolution
    world_y = metadata.origin_y + (point.y + 0.5) * metadata.resolution
    return world_x, world_y


def path_to_world(
    result: PathResult, metadata: GridMetadata
) -> list[tuple[float, float]]:
    """Convert a Core :class:`PathResult` into a list of world waypoints.

    Returns an empty list when no path was found.
    """
    if not result.found:
        return []
    return [cell_to_world(point, metadata) for point in result.path]
