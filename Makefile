# Robot-Pathfinding-ROS2-Simulation — developer task runner.
#
# Target names mirror Robot-Pathfinding-Core so muscle-memory transfers between
# the two repos. The bodies are ROS 2 / colcon aware (Core is hatchling/pytest).
.DEFAULT_GOAL := check
ROS_DISTRO ?= jazzy
PYTHON ?= python3

.PHONY: install lint format format-check typecheck test check build clean

## Install dev tooling, resolve ROS deps, and build the workspace.
install:
	$(PYTHON) -m pip install -r requirements-dev.txt
	$(PYTHON) -m pip install "git+https://github.com/Ricsi1231/Robot-Pathfinding-Core.git"
	rosdep install --from-paths src --ignore-src -r -y
	colcon build --symlink-install
	pre-commit install

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

# Scoped to pure-logic modules: rclpy / ROS message type stubs are incomplete,
# so type-checking node code under --strict produces noise. The grid adapter is
# the typed seam to Robot-Pathfinding-Core and is where typing matters most.
typecheck:
	mypy

# Run pytest directly (like Core). Assumes the workspace is built and sourced
# (`make build && source install/setup.bash`) so package imports resolve.
# colcon test is avoided: its ament_python step uses unittest, which does not
# collect plain pytest functions.
test:
	pytest src

check: lint format-check typecheck test

build:
	colcon build --symlink-install

clean:
	rm -rf build install log .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
