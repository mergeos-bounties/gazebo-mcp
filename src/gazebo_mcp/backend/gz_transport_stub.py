"""Stub implementation mimicking gz-transport API for CI/testing.

Returns deterministic responses without requiring a live Gazebo process.
"""

from __future__ import annotations

import time
from typing import Any


class GzTransportStub:
    """Mimics gz-transport API without a live Gazebo process."""

    def __init__(self) -> None:
        self._models: dict[str, dict[str, Any]] = {
            "ground_plane": {
                "name": "ground_plane",
                "type": "plane",
                "pose": {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0},
            },
        }
        self._paused = False
        self._t0 = time.time()
        self._sim_time = 0.0
        self._worlds = [
            {"name": "default", "active": True},
            {"name": "shapes_demo", "active": False},
        ]

    # --- Model operations ---

    def list_models(self, topic: str = "/model") -> list[dict[str, Any]]:
        """List models in the current world."""
        return list(self._models.values())

    def spawn_model(
        self,
        sdf: str,
        name: str,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.5,
        yaw: float = 0.0,
    ) -> dict[str, Any]:
        """Spawn a model (stub: just records it)."""
        if name in self._models:
            return {"ok": False, "error": f"model '{name}' already exists"}
        self._models[name] = {
            "name": name,
            "type": "box",
            "pose": {"x": x, "y": y, "z": z, "yaw": yaw},
            "twist": {"linear": {"x": 0.0, "y": 0.0, "z": 0.0},
                      "angular": {"x": 0.0, "y": 0.0, "z": 0.0}},
        }
        return {"ok": True, "model": self._models[name]}

    def delete_model(self, name: str) -> dict[str, Any]:
        """Delete a model by name."""
        if name == "ground_plane":
            return {"ok": False, "error": "cannot delete ground_plane"}
        if name not in self._models:
            return {"ok": False, "error": f"unknown model '{name}'"}
        del self._models[name]
        return {"ok": True, "deleted": name}

    # --- Pose operations ---

    def get_pose(self, model_name: str, reference_frame: str = "") -> dict[str, Any]:
        """Get model pose."""
        m = self._models.get(model_name)
        if not m:
            return {"ok": False, "error": f"unknown model '{model_name}'"}
        return {"ok": True, "name": model_name, "pose": m["pose"]}

    def set_pose(
        self,
        model_name: str,
        x: float,
        y: float,
        z: float,
        yaw: float = 0.0,
    ) -> dict[str, Any]:
        """Set model pose."""
        m = self._models.get(model_name)
        if not m:
            return {"ok": False, "error": f"unknown model '{model_name}'"}
        m["pose"] = {"x": x, "y": y, "z": z, "yaw": yaw}
        return {"ok": True, "name": model_name, "pose": m["pose"]}

    # --- Simulation control ---

    def pause(self) -> dict[str, Any]:
        """Pause simulation."""
        self._paused = True
        return {"ok": True, "paused": True, "sim_time_sec": round(self._sim_time, 3)}

    def unpause(self) -> dict[str, Any]:
        """Unpause simulation."""
        self._paused = False
        self._t0 = time.time() - self._sim_time
        return {"ok": True, "paused": False}

    def step(self, num_steps: int = 1) -> dict[str, Any]:
        """Step physics N times."""
        n = max(1, int(num_steps))
        self._sim_time += 0.001 * n
        self._paused = True
        return {"ok": True, "steps": n, "sim_time_sec": round(self._sim_time, 3), "paused": True}

    # --- World operations ---

    def world_info(self) -> dict[str, Any]:
        """Current world info."""
        return {
            "world": "default",
            "paused": self._paused,
            "sim_time_sec": round(self._sim_time, 3),
            "model_count": len(self._models),
        }

    def list_worlds(self) -> list[dict[str, Any]]:
        """List available worlds."""
        return self._worlds
