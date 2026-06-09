"""ament_python build configuration for robot_pathfinding_description."""

from glob import glob

from setuptools import find_packages, setup

package_name = "robot_pathfinding_description"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/urdf", glob("urdf/*")),
        (f"share/{package_name}/worlds", glob("worlds/*")),
        (f"share/{package_name}/models", glob("models/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Ricsi1231",
    maintainer_email="richardnagy551@gmail.com",
    description="Robot URDF and Gazebo world for the pathfinding simulation.",
    license="MIT",
)
