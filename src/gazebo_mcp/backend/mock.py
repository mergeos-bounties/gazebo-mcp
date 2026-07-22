"""Offline Gazebo-style world mock."""

from __future__ import annotations

import random
import time
from typing import Any


class MockBackend:
    name = "mock"
    _SENSOR_TYPES = ("camera", "lidar", "imu", "depth_camera")

    def __init__(self) -> None:
        self.seed_demo()

    def seed_demo(self, profile: str = "default") -> dict[str, Any]:
        profile = (profile or "default").strip().lower()
        self._world = "fleet_demo" if profile == "fleet" else "shapes_demo"
        self._paused = False
        self._t0 = time.time()
        self._sim_time = 0.0
        self._models = self._seed_models(profile)
        self._sensors = self._seed_sensors()
        self._sensor_counter = len(self._sensors)
        return {
            "ok": True,
            "profile": profile,
            "world": self._world,
            "models": list(self._models),
        }

    def _seed_sensors(self) -> dict[str, dict[str, Any]]:
        return {
            "front_camera": {
                "name": "front_camera",
                "type": "camera",
                "parent": "box_1",
                "pose": {"x": 1.0, "y": 0.0, "z": 1.0, "yaw": 0.0},
            },
            "lidar_top": {
                "name": "lidar_top",
                "type": "lidar",
                "parent": None,
                "pose": {"x": 0.0, "y": 0.0, "z": 2.0, "yaw": 0.0},
            },
            "imu_body": {
                "name": "imu_body",
                "type": "imu",
                "parent": "box_1",
                "pose": {"x": 1.0, "y": 0.0, "z": 0.5, "yaw": 0.0},
            },
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

    # ── sensor tools ──────────────────────────────────────────────────

    def list_sensors(self) -> dict[str, Any]:
        """Return all sensors attached to models or free in the world."""
        return {
            "ok": True,
            "sensor_count": len(self._sensors),
            "sensors": list(self._sensors.values()),
        }

    def sensor_snapshot(
        self,
        sensor_name: str,
        resolution: str | None = None,
    ) -> dict[str, Any]:
        """Return synthetic sensor frame."""
        sensor = self._sensors.get(sensor_name)
        if not sensor:
            return {"ok": False, "error": f"unknown sensor {sensor_name}"}
        s_type = sensor["type"]
        if s_type == "camera":
            return self._camera_frame(sensor, resolution)
        if s_type == "depth_camera":
            return self._depth_frame(sensor, resolution)
        if s_type == "lidar":
            return self._lidar_scan(sensor)
        if s_type == "imu":
            return self._imu_data(sensor)
        return {"ok": False, "error": f"unsupported sensor type {s_type}"}

    def sensor_snapshot_all(
        self,
        sensor_types: str | None = None,
    ) -> dict[str, Any]:
        """Return snapshots for all sensors, optionally filtered by type."""
        wanted: set[str] | None
        if sensor_types:
            wanted = set(sensor_types.replace(",", " ").split())
            wanted = wanted & set(self._SENSOR_TYPES)
        else:
            wanted = set(self._SENSOR_TYPES)
        frames: dict[str, Any] = {}
        for name, s in self._sensors.items():
            if s["type"] in wanted:
                frames[name] = self.sensor_snapshot(name)
        return {"ok": True, "sensor_count": len(frames), "frames": frames}

    def _camera_frame(self, sensor: dict[str, Any], resolution: str | None) -> dict[str, Any]:
        w, h = _parse_resolution(resolution, 640, 480)
        rng = random.Random(hash(sensor["name"]))
        return {
            "ok": True,
            "sensor": sensor["name"],
            "type": "camera",
            "timestamp_sec": round(self._sim_time if self._paused else time.time() - self._t0, 3),
            "format": "rgb8",
            "width": w,
            "height": h,
            "step": w * 3,
            "data_length": w * h * 3,
            "mock_data_hash": hex(rng.getrandbits(64)),
            "pose": sensor.get("pose"),
        }

    def _depth_frame(self, sensor: dict[str, Any], resolution: str | None) -> dict[str, Any]:
        w, h = _parse_resolution(resolution, 320, 240)
        return {
            "ok": True,
            "sensor": sensor["name"],
            "type": "depth_camera",
            "format": "32FC1",
            "width": w,
            "height": h,
            "step": w * 4,
            "data_length": w * h * 4,
            "unit": "meters",
            "near_m": 0.1,
            "far_m": 30.0,
            "pose": sensor.get("pose"),
        }

    def _lidar_scan(self, sensor: dict[str, Any]) -> dict[str, Any]:
        return {
            "ok": True,
            "sensor": sensor["name"],
            "type": "lidar",
            "sim_time_sec": round(self._sim_time, 3),
            "ranges": [],
            "intensities": [],
            "range_min_m": 0.1,
            "range_max_m": 30.0,
            "angle_min_rad": -3.14,
            "angle_max_rad": 3.14,
            "angle_increment_rad": 0.01745,
            "point_count": 360,
            "pose": sensor.get("pose"),
        }

    def _imu_data(self, sensor: dict[str, Any]) -> dict[str, Any]:
        return {
            "ok": True,
            "sensor": sensor["name"],
            "type": "imu",
            "sim_time_sec": self._sim_time,
            "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
            "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
            "linear_acceleration": {"x": 0.0, "y": 0.0, "z": 9.8},
            "pose": sensor.get("pose"),
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


def _parse_resolution(resolution: str | None, default_w: int, default_h: int) -> tuple[int, int]:
    """Parse a resolution string like '640x480' into (w, h)."""
    if not resolution:
        return default_w, default_h
    parts = resolution.lower().replace("\uff58", "x").split("x")
    try:
        if len(parts) >= 2:
            return int(parts[0]), int(parts[1])
    except ValueError:
        pass
    return default_w, default_h