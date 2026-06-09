"""Unit tests for the pure-logic grid adapter (no ROS required).

These mirror Core's test style: flat ``test_*`` functions using plain ``assert``.
They exercise the seam against the *real* Robot-Pathfinding-Core API, so they
double as an integration check that Core is installed and behaves as expected.
"""

from __future__ import annotations

from robot_pathfinding import AStarPathfinder, Grid, PathResult, Point

from robot_pathfinding_nav.grid_adapter import (
    GridMetadata,
    cell_to_world,
    occupancy_to_grid,
    path_to_world,
    world_to_cell,
)

META = GridMetadata(width=3, height=3, resolution=1.0, origin_x=0.0, origin_y=0.0)


def test_occupancy_to_grid_marks_obstacles() -> None:
    # Centre cell (1, 1) occupied; everything else free.
    data = [0, 0, 0, 0, 100, 0, 0, 0, 0]
    grid = occupancy_to_grid(data, META)
    assert isinstance(grid, Grid)
    assert grid.is_obstacle(Point(1, 1))
    assert grid.is_walkable(Point(0, 0))


def test_unknown_cells_blocked_by_default() -> None:
    data = [-1] * 9
    grid = occupancy_to_grid(data, META)
    assert not grid.is_walkable(Point(0, 0))


def test_unknown_cells_free_when_opted_out() -> None:
    data = [-1] * 9
    grid = occupancy_to_grid(data, META, unknown_is_obstacle=False)
    assert grid.is_walkable(Point(0, 0))


def test_occupancy_length_mismatch_raises() -> None:
    try:
        occupancy_to_grid([0, 0], META)
    except ValueError:
        return
    raise AssertionError("expected ValueError for mismatched data length")


def test_world_and_cell_roundtrip() -> None:
    meta = GridMetadata(width=10, height=10, resolution=0.5, origin_x=-1.0)
    cell = world_to_cell(1.25, 0.75, meta)
    world_x, world_y = cell_to_world(cell, meta)
    # Re-deriving the cell from the centre returns the same cell.
    assert world_to_cell(world_x, world_y, meta) == cell


def test_path_to_world_empty_when_not_found() -> None:
    assert path_to_world(PathResult(found=False), META) == []


def test_end_to_end_plan_against_core() -> None:
    # Free 3x3 grid: A* should find a path from corner to corner.
    data = [0] * 9
    grid = occupancy_to_grid(data, META)
    result = AStarPathfinder().find_path(grid, Point(0, 0), Point(2, 2))
    assert result.found
    waypoints = path_to_world(result, META)
    assert len(waypoints) == result.path_length
    assert waypoints[0] == (0.5, 0.5)
