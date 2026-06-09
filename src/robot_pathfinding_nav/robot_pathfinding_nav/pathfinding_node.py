"""ROS 2 node that plans grid paths using Robot-Pathfinding-Core.

The node keeps the latest map and robot pose, and replans whenever a new goal
arrives. All non-ROS logic lives in :mod:`robot_pathfinding_nav.grid_adapter`
and in the Core library, keeping this file a thin ROS adapter.
"""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid, Odometry, Path
from rclpy.node import Node
from robot_pathfinding import (
    AStarPathfinder,
    BasePathfinder,
    BfsPathfinder,
    DfsPathfinder,
    DijkstraPathfinder,
    PathResult,
)

from robot_pathfinding_nav.grid_adapter import (
    GridMetadata,
    occupancy_to_grid,
    path_to_world,
    world_to_cell,
)

# Maps the `algorithm` parameter string to a Core pathfinder factory.
_ALGORITHMS: dict[str, type[BasePathfinder]] = {
    "astar": AStarPathfinder,
    "bfs": BfsPathfinder,
    "dfs": DfsPathfinder,
    "dijkstra": DijkstraPathfinder,
}


class PathfindingNode(Node):
    """Subscribes to map, odometry, and goal; publishes a planned path."""

    def __init__(self) -> None:
        super().__init__("pathfinding_node")

        self.declare_parameter("algorithm", "astar")
        self.declare_parameter("allow_diagonal", True)
        self.declare_parameter("occupied_threshold", 50)

        algorithm = self.get_parameter("algorithm").value
        pathfinder_cls = _ALGORITHMS.get(algorithm, AStarPathfinder)
        if algorithm not in _ALGORITHMS:
            self.get_logger().warn(
                f"unknown algorithm '{algorithm}', falling back to astar"
            )
        self._pathfinder: BasePathfinder = pathfinder_cls()

        self._map: OccupancyGrid | None = None
        self._pose: PoseStamped | None = None

        self.create_subscription(OccupancyGrid, "/map", self._on_map, 1)
        self.create_subscription(Odometry, "/odom", self._on_odom, 10)
        self.create_subscription(PoseStamped, "/goal_pose", self._on_goal, 10)
        self._plan_pub = self.create_publisher(Path, "/plan", 1)

        self.get_logger().info(
            f"pathfinding_node ready (algorithm={self._pathfinder.name()})"
        )

    def _on_map(self, msg: OccupancyGrid) -> None:
        self._map = msg

    def _on_odom(self, msg: Odometry) -> None:
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose
        self._pose = pose

    def _on_goal(self, goal: PoseStamped) -> None:
        if self._map is None:
            self.get_logger().warn("no map received yet; ignoring goal")
            return
        if self._pose is None:
            self.get_logger().warn("no robot pose received yet; ignoring goal")
            return

        metadata = GridMetadata(
            width=self._map.info.width,
            height=self._map.info.height,
            resolution=self._map.info.resolution,
            origin_x=self._map.info.origin.position.x,
            origin_y=self._map.info.origin.position.y,
        )
        grid = occupancy_to_grid(
            self._map.data,
            metadata,
            occupied_threshold=self.get_parameter("occupied_threshold").value,
            allow_diagonal=self.get_parameter("allow_diagonal").value,
        )

        start = world_to_cell(
            self._pose.pose.position.x, self._pose.pose.position.y, metadata
        )
        goal_cell = world_to_cell(
            goal.pose.position.x, goal.pose.position.y, metadata
        )

        result = self._pathfinder.find_path(grid, start, goal_cell)
        if not result.found:
            self.get_logger().warn(
                f"no path from {start} to {goal_cell} "
                f"({result.visited_nodes} nodes explored)"
            )
            self._plan_pub.publish(self._empty_path())
            return

        self.get_logger().info(
            f"path found: {result.path_length} cells, "
            f"{result.visited_nodes} explored, {result.execution_time_ms:.2f} ms"
        )
        self._plan_pub.publish(self._build_path(result, metadata))

    def _build_path(self, result: PathResult, metadata: GridMetadata) -> Path:
        path = Path()
        path.header.frame_id = "map"
        path.header.stamp = self.get_clock().now().to_msg()
        for world_x, world_y in path_to_world(result, metadata):
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = world_x
            pose.pose.position.y = world_y
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        return path

    def _empty_path(self) -> Path:
        path = Path()
        path.header.frame_id = "map"
        path.header.stamp = self.get_clock().now().to_msg()
        return path


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = PathfindingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
