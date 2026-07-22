"""FastMCP server: Gazebo tools for AI agents."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from gazebo_mcp.backend import get_backend, switch_mode
from gazebo_mcp.config import get_mode

mcp = FastMCP(
    "gazebo-mcp",
    instructions=(
        "Gazebo / gz-sim MCP server. Prefer mock mode offline. "
        "Typical flow: gazebo_doctor → gazebo_world_info → gazebo_list_models → gazebo_spawn."
    ),
)


def _j(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


@mcp.tool()
def gazebo_mode(mode: str | None = None) -> str:
    """Get or set Gazebo backend mode (mock|live)."""
    if mode:
        return _j(switch_mode(mode))
    b = get_backend()
    return _j({"mode": get_mode(), "backend": b.name, "doctor": b.doctor()})


@mcp.tool()
def gazebo_doctor() -> str:
    """Check mock/live Gazebo connectivity."""
    return _j(get_backend().doctor())


@mcp.tool()
def gazebo_seed_demo() -> str:
    """Reset the mock Gazebo shapes world (mock only)."""
    return _j(get_backend().seed_demo())


@mcp.tool()
def gazebo_world_info() -> str:
    """World name, pause state, sim time."""
    return _j(get_backend().world_info())


@mcp.tool()
def gazebo_world_list() -> str:
    """List available worlds and identify the active world."""
    return _j(get_backend().list_worlds())


@mcp.tool()
def gazebo_list_models() -> str:
    """List models in the current world."""
    return _j(get_backend().list_models())


@mcp.resource("gazebo://world")
def world_snapshot() -> str:
    """Snapshot of the current Gazebo world: models, poses, sim time, physics."""
    return _j(get_backend().snapshot())


@mcp.tool()
def gazebo_spawn(
    name: str,
    model_type: str = "box",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.5,
    yaw: float = 0.0,
) -> str:
    """Spawn a model at pose."""
    return _j(get_backend().spawn(name, model_type, x, y, z, yaw))


@mcp.tool()
def gazebo_delete(name: str) -> str:
    """Delete a model by name."""
    return _j(get_backend().delete(name))


@mcp.tool()
def gazebo_get_pose(name: str) -> str:
    """Get model pose."""
    return _j(get_backend().get_pose(name))


@mcp.tool()
def gazebo_set_pose(
    name: str,
    x: float,
    y: float,
    z: float,
    yaw: float = 0.0,
    linear_x: float = 0.0,
    linear_y: float = 0.0,
    linear_z: float = 0.0,
    angular_x: float = 0.0,
    angular_y: float = 0.0,
    angular_z: float = 0.0,
) -> str:
    """Set model pose and optional linear/angular velocity metadata."""
    return _j(
        get_backend().set_pose(
            name,
            x,
            y,
            z,
            yaw,
            {"x": linear_x, "y": linear_y, "z": linear_z},
            {"x": angular_x, "y": angular_y, "z": angular_z},
        )
    )


@mcp.tool()
def gazebo_pause() -> str:
    """Pause simulation."""
    return _j(get_backend().pause())


@mcp.tool()
def gazebo_unpause() -> str:
    """Unpause simulation."""
    return _j(get_backend().unpause())


@mcp.tool()
def gazebo_step(steps: int = 1) -> str:
    """Step the physics engine N times (leaves sim paused)."""
    return _j(get_backend().step(steps))


# ── sensor tools ──────────────────────────────────────────────────


@mcp.tool()
def gazebo_list_sensors() -> str:
    """List all sensors in the current world."""
    return _j(get_backend().list_sensors())


@mcp.tool()
def gazebo_sensor_snapshot(
    sensor_name: str,
    resolution: str | None = None,
) -> str:
    """Capture a synthetic sensor frame (camera, lidar, imu, depth_camera)."""
    return _j(get_backend().sensor_snapshot(sensor_name, resolution))


@mcp.tool()
def gazebo_sensor_snapshot_all(
    sensor_types: str | None = None,
) -> str:
    """Capture frames for all sensors, optionally filtered by type."""
    return _j(get_backend().sensor_snapshot_all(sensor_types))


def run_stdio() -> None:
    mcp.run(transport="stdio")