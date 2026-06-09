"""Launch only the pathfinding node (no Gazebo).

Useful for replaying a recorded map/odom bag or driving the planner from another
map source without starting the simulator.
"""

from __future__ import annotations

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    algorithm = LaunchConfiguration("algorithm")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "algorithm",
                default_value="astar",
                description="Core pathfinder: astar | bfs | dfs | dijkstra",
            ),
            Node(
                package="robot_pathfinding_nav",
                executable="pathfinding_node",
                output="screen",
                parameters=[{"algorithm": algorithm}],
            ),
        ]
    )
