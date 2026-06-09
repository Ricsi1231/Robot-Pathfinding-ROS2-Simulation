# Robot-Pathfinding-ROS2-Simulation

ROS 2 + Gazebo simulation that drives a mobile robot through a 2D world using the
pathfinding algorithms from
[**Robot-Pathfinding-Core**](https://github.com/Ricsi1231/Robot-Pathfinding-Core).
The Core library stays a pure, dependency-free Python package; this repo is the
robotics integration layer around it.

The two repos deliberately share the **same developer-facing structure** —
identical `Makefile` targets, the same `ruff` configuration, `pre-commit` hooks,
and CI shape — so they feel like one project. Where ROS 2 imposes its own
conventions (colcon build, `package.xml`, `ament_python`), the build layer
adapts; everything else mirrors Core.

## Features

- **Multi-package colcon workspace** — clean separation of concerns:
  - `robot_pathfinding_nav` — the ROS 2 node that wraps Core and plans paths.
  - `robot_pathfinding_description` — robot URDF and the Gazebo world.
  - `robot_pathfinding_bringup` — launch files and the ROS ↔ Gazebo bridge.
- **Typed seam to Core** — `grid_adapter.py` converts a `nav_msgs/OccupancyGrid`
  into a `robot_pathfinding.Grid` and a returned `PathResult` back into a
  `nav_msgs/Path`. It is pure logic, unit-tested, and `mypy`-checked.
- **Pluggable algorithms** — A\*, BFS, DFS, and Dijkstra are all selectable via a
  node parameter, backed directly by Core's pathfinders.
- **Same dev workflow as Core** — `make check` runs lint, format-check,
  type-check, and tests.

## Prerequisites

- **ROS 2 Jazzy Jalisco** (Ubuntu 24.04, Python 3.12)
- **Gazebo Harmonic** with the `ros_gz` integration packages
- `rosdep`, `colcon`, and `pip`

## Install & build

```bash
# from the repository root, with ROS 2 Jazzy sourced
make install
source install/setup.bash
```

`make install` installs dev tooling, installs Core from GitHub, resolves ROS
dependencies with `rosdep`, builds the workspace with `colcon`, and installs the
pre-commit hook.

## Run

```bash
ros2 launch robot_pathfinding_bringup simulation.launch.py
```

This starts Gazebo with the grid world, spawns the robot, brings up the
`ros_gz_bridge`, and launches the pathfinding node. Publish a goal and watch the
planned path appear on `/plan`:

```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  '{header: {frame_id: "map"}, pose: {position: {x: 3.0, y: 2.0}}}'
```

## Architecture

```
/map  (nav_msgs/OccupancyGrid) ─┐
                                ├─►  robot_pathfinding_nav
/goal_pose (PoseStamped) ───────┘     │  grid_adapter: OccupancyGrid → Grid
                                      │  Core pathfinder: find_path(...)
                                      │  grid_adapter: PathResult → Path
                                      └─►  /plan (nav_msgs/Path)
```

## Development

```bash
make lint          # ruff check
make format        # ruff format
make typecheck     # mypy (scoped to the grid adapter)
make test          # colcon test
make check         # all of the above
```

## License

MIT — © 2026 Richard. See [LICENSE](LICENSE).
