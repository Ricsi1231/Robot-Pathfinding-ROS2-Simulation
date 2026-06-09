"""ament_python build configuration for robot_pathfinding_nav."""

from setuptools import find_packages, setup

package_name = "robot_pathfinding_nav"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    # robot-pathfinding-core is installed separately via pip (see Makefile / CI);
    # listing it here documents the runtime import dependency.
    install_requires=["setuptools", "robot-pathfinding-core"],
    zip_safe=True,
    maintainer="Ricsi1231",
    maintainer_email="richardnagy551@gmail.com",
    description="ROS 2 pathfinding node wrapping Robot-Pathfinding-Core.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "pathfinding_node = robot_pathfinding_nav.pathfinding_node:main",
        ],
    },
)
