"""Bring up the full pathfinding simulation.

Starts Gazebo Harmonic with the grid world, spawns the robot, runs the ROS-Gazebo
bridge, publishes the robot description, and launches the pathfinding node.
"""

from __future__ import annotations

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    description_share = get_package_share_directory("robot_pathfinding_description")
    bringup_share = get_package_share_directory("robot_pathfinding_bringup")
    ros_gz_sim_share = get_package_share_directory("ros_gz_sim")

    world_path = os.path.join(description_share, "worlds", "grid_world.sdf")
    xacro_path = os.path.join(description_share, "urdf", "robot.urdf.xacro")
    bridge_config = os.path.join(bringup_share, "config", "bridge.yaml")

    robot_description = ParameterValue(
        Command(["xacro ", xacro_path]), value_type=str
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": f"-r {world_path}"}.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "pathfinding_bot",
            "-topic", "robot_description",
            "-z", "0.1",
        ],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{"config_file": bridge_config, "use_sim_time": True}],
        output="screen",
    )

    pathfinding_node = Node(
        package="robot_pathfinding_nav",
        executable="pathfinding_node",
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    return LaunchDescription(
        [
            gz_sim,
            robot_state_publisher,
            spawn_robot,
            bridge,
            pathfinding_node,
        ]
    )
