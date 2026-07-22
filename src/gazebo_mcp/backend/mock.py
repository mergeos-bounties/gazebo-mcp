"""Offline Gazebo-style world mock with graph state tracking."""

from __future__ import annotations

import time
from typing import Any


class MockBackend:
    name = "mock"

    def __init__(self) -> None:
        self.seed_demo()

    def seed_demo(self, profile: str = "default") -> dict[str, Any]:
        profile = (profile or "default").strip().lower()
        self._world = "fleet_demo" if profile == "fleet" else "shapes_demo"
        self._paused = False
        self._t0 = time.time()
        self._sim_time = 0.0
        self._models = self._seed_models(profile)
        self._rebuild_graph()
        return {
            "ok": True,
            "profile": profile,
            "world": self._world,
            "models": list(self._models),
        }

    def _rebuild_graph(self) -> None:
        """Rebuild the world scene graph from current model state."""
        self._graph: dict[str, dict[str, Any]] = {}
        for name, model in self._models.items():
            self._graph[name] = {
                "name": name,
                "type": model.get("type", "unknown"),
                "parent": None,
                "children": [],
                "pose": model.get("pose", {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}),
            }
        # ground_plane acts as the root; all other models are its children
        if "ground_plane" in self._graph:
            for name in self._graph:
                if name != "ground_plane":
                    self._graph["ground_plane"]["children"].append(name)
                    self._graph[name]["parent"] = "ground_plane"

    def graph(self) -> dict[str, Any]:
        """Return the current world scene graph (model hierarchy).

        The graph reflects the parent-child relationships between models.
        Every model spawn and delete automatically rebuilds the graph,
        ensuring state consistency across all tools.
        """
        return {
            "ok": True,
            "mode": "mock",
            "world": self._world,
            "node_count": len(self._graph),
            "nodes": list(self._graph.values()),
        }

    def _seed_models(self, profile: str) -> dict[str, dict[str, Any]]:
        models: dict[str, dict[str, Any]] = {
            "ground_plane": {
                "name": "ground_plane",
                "type": "plane",
                "pose": {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0},
                "twist": self._twist(),
            },
        }
        if profile == "fleet":
            models.update(
                {
                    "robot_0": {
                        "name": "robot_0",
                        "type": "robot",
                        "pose": {"x": -1.0, "y": -1.0, "z": 0.1, "yaw": 0.0},
                    },
                    "robot_1": {
                        "name": "robot_1",
                        "type": "robot",
                        "pose": {"x": 0.0, "y": 1.0, "z": 0.1, "yaw": 1.57},
                    },
                    "robot_2": {
                        "name": "robot_2",
                        "type": "robot",
                        "pose": {"x": 1.0, "y": -1.0, "z": 0.1, "yaw": 3.14},
                    },
                }
            )
            return models
        models.update(
            {
            "box_1": {
                "name": "box_1",
                "type": "box",
                "pose": {"x": 1.0, "y": 0.0, "z": 0.5, "yaw": 0.0},
                "twist": self._twist(),
            },
            "sphere_1": {
                "name": "sphere_1",
                "type": "sphere",
                "pose": {"x": -1.0, "y": 0.5, "z": 0.5, "yaw": 0.0},
                "twist": self._twist(),
            },
            }
        )
        return models

    def _twist(
        self,
        linear_velocity: dict[str, Any] | None = None,
        angular_velocity: dict[str, Any] | None = None,
    ) -> dict[str, dict[str, float]]:
        linear_velocity = linear_velocity or {}
        angular_velocity = angular_velocity or {}
        return {
            "linear": {
                "x": float(linear_velocity.get("x", 0.0)),
                "y": float(linear_velocity.get("y", 0.0)),
                "z": float(linear_velocity.get("z", 0.0)),
            },
            "angular": {
                "x": float(angular_velocity.get("x", 0.0)),
                "y": float(angular_velocity.get("y", 0.0)),
                "z": float(angular_velocity.get("z", 0.0)),
            },
        }

    def doctor(self) -> dict[str, Any]:
        return {
            "ok": True,
            "connected": True,
            "mode": "mock",
            "gazebo_required": False,
            "message": "Mock Gazebo world active — no Gazebo install needed",
            "world": self._world,
            "model_count": len(self._models),
            "paused": self._paused,
            "sim_time_sec": round(self._sim_time, 3),
        }

    def world_info(self) -> dict[str, Any]:
        if not self._paused:
            self._sim_time = time.time() - self._t0
        return {
            "world": self._world,
            "paused": self._paused,
            "sim_time_sec": round(self._sim_time, 3),
            "model_count": len(self._models),
            "physics": "ode-mock",
        }

    def list_worlds(self) -> dict[str, Any]:
        """List deterministic offline world fixtures and mark the active world."""
        worlds = [
            {
                "name": "shapes_demo",
                "profile": "default",
                "model_count": 3,
                "active": self._world == "shapes_demo",
            },
            {
                "name": "fleet_demo",
                "profile": "fleet",
                "model_count": 4,
                "active": self._world == "fleet_demo",
            },
        ]
        return {
            "ok": True,
            "mode": "mock",
            "current_world": self._world,
            "worlds": worlds,
        }

    def list_models(self) -> list[dict[str, Any]]:
        return list(self._models.values())

    def snapshot(self) -> dict[str, Any]:
        """Full world snapshot: models, sim time, physics params."""
        if not self._paused:
            self._sim_time = time.time() - self._t0
        return {
            "ok": True,
            "world": self._world,
            "paused": self._paused,
            "sim_time_sec": round(self._sim_time, 3),
            "model_count": len(self._models),
            "models": list(self._models.values()),
            "physics": {
                "engine": "ode-mock",
                "max_step_size": 0.001,
                "real_time_factor": 1.0,
                "gravity": {"x": 0.0, "y": 0.0, "z": -9.8},
            },
        }

    def spawn(
        self,
        name: str,
        model_type: str,
        x: float,
        y: float,
        z: float,
        yaw: float = 0.0,
    ) -> dict[str, Any]:
        if name in self._models:
            return {"ok": False, "error": f"model {name} already exists"}
        self._models[name] = {
            "name": name,
            "type": model_type or "box",
            "pose": {"x": float(x), "y": float(y), "z": float(z), "yaw": float(yaw)},
            "twist": self._twist(),
        }
        self._rebuild_graph()
        return {"ok": True, "model": self._models[name]}

    def delete(self, name: str) -> dict[str, Any]:
        if name not in self._models:
            return {"ok": False, "error": f"unknown model {name}"}
        if name == "ground_plane":
            return {"ok": False, "error": "cannot delete ground_plane"}
        del self._models[name]
        self._rebuild_graph()
        return {"ok": True, "deleted": name}

    def get_pose(self, name: str) -> dict[str, Any]:
        m = self._models.get(name)
        if not m:
            return {"ok": False, "error": f"unknown model {name}"}
        return {"ok": True, "name": name, "pose": m["pose"], "twist": m.get("twist", self._twist())}

    def set_pose(
        self,
        name: str,
        x: float,
        y: float,
        z: float,
        yaw: float = 0.0,
        linear_velocity: dict[str, Any] | None = None,
        angular_velocity: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        m = self._models.get(name)
        if not m:
            return {"ok": False, "error": f"unknown model {name}"}
        m["pose"] = {"x": float(x), "y": float(y), "z": float(z), "yaw": float(yaw)}
        m["twist"] = self._twist(linear_velocity, angular_velocity)
        return {"ok": True, "name": name, "pose": m["pose"], "twist": m["twist"]}

    def pause(self) -> dict[str, Any]:
        self._paused = True
        return {"ok": True, "paused": True, "sim_time_sec": round(self._sim_time, 3)}

    def unpause(self) -> dict[str, Any]:
        self._paused = False
        self._t0 = time.time() - self._sim_time
        return {"ok": True, "paused": False}

    def step(self, steps: int = 1) -> dict[str, Any]:
        n = max(1, int(steps))
        self._sim_time += 0.001 * n
        self._paused = True
        return {"ok": True, "steps": n, "sim_time_sec": round(self._sim_time, 3), "paused": True}
    def sensor_snapshot(self, sensor_type: str = "lidar", name: str | None = None) -> dict[str, Any]:
        """Return synthetic sensor frame data for agent workflows.

        Args:
            sensor_type: Type of sensor ("lidar", "camera", "depth", "imu").
            name: Optional model name to attach sensor data to.

        Returns:
            Dict with synthetic sensor frame data depending on sensor type.
        """
        sensor_type = (sensor_type or "lidar").strip().lower()
        valid_types = {"lidar", "camera", "depth", "imu"}
        if sensor_type not in valid_types:
            return {"ok": False, "error": f"unsupported sensor_type '{sensor_type}'. Valid: {sorted(valid_types)}"}

        if name is not None and name not in self._models:
            return {"ok": False, "error": f"unknown model {name}"}

        pose = self._models.get(name, {}).get("pose", {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}) if name else {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}

        result: dict[str, Any] = {
            "ok": True,
            "mode": "mock",
            "sensor_type": sensor_type,
            "world": self._world,
            "sim_time_sec": round(self._sim_time, 3),
            "pose": pose,
        }

        if name:
            result["model"] = name

        if sensor_type == "lidar":
            result["data"] = {
                "num_points": 360,
                "range_min": 0.1,
                "range_max": 30.0,
                "angle_min_rad": -3.14159,
                "angle_max_rad": 3.14159,
                "points": [
                    {"angle_deg": i, "distance_m": round(5.0 + 3.0 * (i % 7) / 7.0, 3), "intensity": round(0.5 + 0.5 * (i % 3) / 3.0, 3)}
                    for i in range(0, 360, 10)
                ],
            }
        elif sensor_type == "camera":
            result["data"] = {
                "width": 640,
                "height": 480,
                "fov_deg": 90.0,
                "format": "RGB8",
                "frame_id": f"camera_frame_{int(self._sim_time * 30)}",
                "timestamp_sec": round(self._sim_time, 3),
            }
        elif sensor_type == "depth":
            result["data"] = {
                "width": 320,
                "height": 240,
                "fov_deg": 87.0,
                "format": "F32",
                "range_min": 0.2,
                "range_max": 10.0,
                "frame_id": f"depth_frame_{int(self._sim_time * 30)}",
                "timestamp_sec": round(self._sim_time, 3),
            }
        elif sensor_type == "imu":
            result["data"] = {
                "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
                "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
                "linear_acceleration": {"x": 0.0, "y": 0.0, "z": -9.8},
                "frame_id": f"imu_frame_{int(self._sim_time * 30)}",
                "timestamp_sec": round(self._sim_time, 3),
            }

        return result
