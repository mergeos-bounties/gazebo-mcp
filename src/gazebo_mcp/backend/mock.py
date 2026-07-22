"""Offline Gazebo-style world mock."""

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
        return {
            "ok": True,
            "profile": profile,
            "world": self._world,
            "models": list(self._models),
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
        return {"ok": True, "model": self._models[name]}

    def delete(self, name: str) -> dict[str, Any]:
        if name not in self._models:
            return {"ok": False, "error": f"unknown model {name}"}
        if name == "ground_plane":
            return {"ok": False, "error": "cannot delete ground_plane"}
        del self._models[name]
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

    def sensor_snapshot(self, sensor_type: str = "lidar", count: int = 1) -> dict[str, Any]:
        """Return synthetic sensor frames for agent workflows.
        
        Supports: lidar, camera, depth, thermal
        
        Returns deterministic mock frames with schema documentation.
        See docs/sensor-snapshot.md for full schema.
        """
        import random
        random.seed(hash(sensor_type) + count)
        
        frame_schema = {
            "sensor_type": sensor_type,
            "count": count,
            "frames": []
        }
        
        for i in range(count):
            if sensor_type == "lidar":
                frame = {
                    "frame_id": f"lidar_{i}",
                    "timestamp": round(self._sim_time + i * 0.01, 6),
                    "type": "lidar_scan",
                    "ranges": [round(random.uniform(0.5, 10.0), 3) for _ in range(360)],
                    "angle_min": -3.14159,
                    "angle_max": 3.14159,
                    "angle_increment": 0.01745,
                    "width": 360,
                    "height": 1,
                    "frame_status": "ok"
                }
            elif sensor_type == "camera":
                frame = {
                    "frame_id": f"camera_{i}",
                    "timestamp": round(self._sim_time + i * 0.033, 6),
                    "type": "image_frame",
                    "width": 640,
                    "height": 480,
                    "encoding": "rgb8",
                    "step": 640 * 3,
                    "data_size": 640 * 480 * 3,
                    "camera_info": {
                        "K": [525.0, 0, 320, 0, 525.0, 240, 0, 0, 1],
                        "D": [0, 0, 0, 0, 0],
                        "R": [1, 0, 0, 0, 1, 0, 0, 0, 1],
                        "P": [525.0, 0, 320, 0, 0, 525.0, 240, 0, 0, 0, 1, 0]
                    },
                    "pose": {
                        "position": {"x": round(random.uniform(-5, 5), 3), 
                                     "y": round(random.uniform(-5, 5), 3), 
                                     "z": round(random.uniform(0.5, 3), 3)},
                        "orientation": {"x": 0, "y": 0, "z": 0, "w": 1}
                    },
                    "frame_status": "ok"
                }
            elif sensor_type == "depth":
                frame = {
                    "frame_id": f"depth_{i}",
                    "timestamp": round(self._sim_time + i * 0.033, 6),
                    "type": "depth_frame",
                    "width": 640,
                    "height": 480,
                    "encoding": "32FC1",
                    "step": 640 * 4,
                    "data_size": 640 * 480 * 4,
                    "min_range": 0.1,
                    "max_range": 30.0,
                    "frame_status": "ok"
                }
            elif sensor_type == "thermal":
                frame = {
                    "frame_id": f"thermal_{i}",
                    "timestamp": round(self._sim_time + i * 0.033, 6),
                    "type": "thermal_frame",
                    "width": 320,
                    "height": 240,
                    "encoding": "mono16",
                    "min_temp": -20.0,
                    "max_temp": 100.0,
                    "emissivity": 0.95,
                    "frame_status": "ok"
                }
            else:
                frame = {
                    "frame_id": f"{sensor_type}_{i}",
                    "timestamp": round(self._sim_time + i * 0.01, 6),
                    "type": sensor_type,
                    "data": {},
                    "frame_status": "ok"
                }
            frame_schema["frames"].append(frame)
        
        return frame_schema
