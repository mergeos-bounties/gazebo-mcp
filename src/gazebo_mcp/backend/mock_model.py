"""Mock model lifecycle tools for gazebo-mcp.

Provides standalone mock functions for spawning and deleting models,
with state consistency guaranteed across tool calls.
"""

from __future__ import annotations

from typing import Any

# Shared mock state — guaranteed consistent across all tools
_mock_world: dict[str, dict[str, Any]] = {}
_graph_version: int = 0


def _init_default_world() -> None:
    """Initialize the mock world with default fixtures if empty."""
    global _mock_world, _graph_version  # noqa: PLW0603
    if _mock_world:
        return
    _mock_world = {
        "ground_plane": {
            "name": "ground_plane",
            "type": "plane",
            "pose": {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0},
            "twist": {
                "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
                "angular": {"x": 0.0, "y": 0.0, "z": 0.0},
            },
        },
        "box_1": {
            "name": "box_1",
            "type": "box",
            "pose": {"x": 1.0, "y": 0.0, "z": 0.5, "yaw": 0.0},
            "twist": {
                "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
                "angular": {"x": 0.0, "y": 0.0, "z": 0.0},
            },
        },
        "sphere_1": {
            "name": "sphere_1",
            "type": "sphere",
            "pose": {"x": -1.0, "y": 0.5, "z": 0.5, "yaw": 0.0},
            "twist": {
                "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
                "angular": {"x": 0.0, "y": 0.0, "z": 0.0},
            },
        },
    }
    _graph_version = 1


def mock_spawn_model(
    name: str,
    model_type: str = "box",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.5,
    yaw: float = 0.0,
) -> dict[str, Any]:
    """Spawn a model into the mock Gazebo world.

    Updates the scene graph so all subsequent tool calls (list, snapshot)
    see the new model.

    Args:
        name: Unique model name (required).
        model_type: Model kind — box, sphere, cylinder, plane, robot, urdf.
        x, y, z: Spawn position in meters.
        yaw: Yaw rotation in radians.

    Returns:
        Dict with status and the created model entry.
    """
    global _graph_version  # noqa: PLW0603
    _init_default_world()

    if name in _mock_world:
        return {
            "ok": False,
            "error": f"model '{name}' already exists",
            "graph_version": _graph_version,
        }

    allowed_types = {"box", "sphere", "cylinder", "plane", "robot", "urdf"}
    if model_type not in allowed_types:
        return {
            "ok": False,
            "error": f"model_type '{model_type}' not in allowed set",
            "allowed_types": sorted(allowed_types),
            "graph_version": _graph_version,
        }

    _mock_world[name] = {
        "name": name,
        "type": model_type,
        "pose": {
            "x": float(x),
            "y": float(y),
            "z": float(z),
            "yaw": float(yaw),
        },
        "twist": {
            "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": 0.0},
        },
    }
    _graph_version += 1

    return {
        "ok": True,
        "model": _mock_world[name],
        "graph_version": _graph_version,
    }


def mock_delete_model(name: str) -> dict[str, Any]:
    """Delete a model from the mock Gazebo world.

    Updates the scene graph so all subsequent tool calls reflect the deletion.

    Args:
        name: Model name to remove.

    Returns:
        Dict with status.
    """
    global _graph_version  # noqa: PLW0603
    _init_default_world()

    if name not in _mock_world:
        return {
            "ok": False,
            "error": f"unknown model '{name}'",
            "graph_version": _graph_version,
        }

    if name == "ground_plane":
        return {
            "ok": False,
            "error": "cannot delete ground_plane",
            "graph_version": _graph_version,
        }

    deleted = _mock_world.pop(name)
    _graph_version += 1

    return {
        "ok": True,
        "deleted": name,
        "was_type": deleted["type"],
        "graph_version": _graph_version,
        "remaining_models": list(_mock_world.keys()),
    }


def mock_list_models() -> dict[str, Any]:
    """List all models currently in the mock world.

    Returns state consistent with prior spawn/delete operations.
    """
    _init_default_world()
    return {
        "ok": True,
        "models": list(_mock_world.values()),
        "model_count": len(_mock_world),
        "graph_version": _graph_version,
    }


def mock_reset_world() -> dict[str, Any]:
    """Reset the mock world to default state (for testing consistency)."""
    global _mock_world, _graph_version  # noqa: PLW0603
    _mock_world = {}
    _graph_version = 0
    _init_default_world()
    return {
        "ok": True,
        "models": list(_mock_world.keys()),
        "graph_version": _graph_version,
    }