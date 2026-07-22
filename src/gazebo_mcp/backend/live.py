"""Optional live Gazebo bridge (HTTP/file). Fails closed when unavailable."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from gazebo_mcp.config import bridge_file, bridge_url, spawn_allowlist


class LiveBackend:
    name = "live"

    def _get_json(self, endpoint: str) -> dict[str, Any]:
        url = bridge_url()
        if not url:
            return {
                "ok": False,
                "connected": False,
                "mode": "live",
                "message": "Set GAZEBO_MCP_BRIDGE_URL for live HTTP bridge mode",
            }
        try:
            target = url.rstrip("/") + endpoint
            with urlopen(Request(target, method="GET"), timeout=2) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            return {"ok": False, "connected": False, "mode": "live", "error": str(exc)}

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return {
                "ok": False,
                "connected": False,
                "mode": "live",
                "error": f"bridge returned invalid JSON from {endpoint}: {exc}",
            }
        if not isinstance(data, dict):
            return {
                "ok": False,
                "connected": False,
                "mode": "live",
                "error": f"bridge returned non-object JSON from {endpoint}",
            }
        return data

    def doctor(self) -> dict[str, Any]:
        url = bridge_url()
        path = bridge_file()
        if url:
            data = self._get_json("/health")
            if not data.get("ok", True):
                return data
            return {
                "ok": True,
                "connected": True,
                "mode": "live",
                "bridge": "http",
                "health": data,
            }
        if path and Path(path).is_file():
            return {"ok": True, "connected": True, "mode": "live", "bridge": "file", "path": path}
        return {
            "ok": False,
            "connected": False,
            "mode": "live",
            "message": "Set GAZEBO_MCP_BRIDGE_URL or GAZEBO_MCP_BRIDGE_FILE for live mode",
        }

    def seed_demo(self) -> dict[str, Any]:
        return {"ok": False, "error": "seed_demo is mock-only"}

    def _unsupported(self, op: str) -> dict[str, Any]:
        d = self.doctor()
        if not d.get("ok"):
            return d
        return {"ok": False, "error": f"live {op} not wired — configure bridge endpoints"}

    def world_info(self) -> dict[str, Any]:
        url = bridge_url()
        if url:
            data = self._get_json("/world_info")
            if not data.get("ok", True):
                return data
            return {"ok": True, **data}
        return self._unsupported("world_info")

    def list_worlds(self) -> dict[str, Any]:
        url = bridge_url()
        if not url:
            return self._unsupported("world_list")
        data = self._get_json("/worlds")
        if not data.get("ok", True):
            return data
        if not isinstance(data.get("worlds"), list):
            return {
                "ok": False,
                "connected": False,
                "mode": "live",
                "error": "bridge returned invalid worlds payload",
            }
        return {"ok": True, "mode": "live", **data}

    def list_models(self) -> list[dict[str, Any]]:
        return []

    def snapshot(self) -> dict[str, Any]:
        return self._unsupported("snapshot")

    def spawn(self, name: str, model_type: str, x: float, y: float, z: float, yaw: float = 0.0) -> dict[str, Any]:
        allowed = spawn_allowlist()
        normalized = (model_type or "").strip().lower()
        if allowed is not None and normalized not in allowed:
            return {
                "ok": False,
                "mode": "live",
                "error": f"model_type {model_type!r} is not allowed by GAZEBO_MCP_SPAWN_ALLOWLIST",
                "allowed_model_types": sorted(allowed),
            }
        return self._unsupported("spawn")

    def delete(self, name: str) -> dict[str, Any]:
        return self._unsupported("delete")

    def get_pose(self, name: str) -> dict[str, Any]:
        return self._unsupported("get_pose")

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
        return self._unsupported("set_pose")

    def pause(self) -> dict[str, Any]:
        return self._unsupported("pause")

    def unpause(self) -> dict[str, Any]:
        return self._unsupported("unpause")

    def step(self, steps: int = 1) -> dict[str, Any]:
        return self._unsupported("step")

    def sensor_snapshot(self, sensor_type: str = "lidar", name: str | None = None) -> dict[str, Any]:
        """Return synthetic sensor frame data (live stub — falls back to mock data)."""
        # Live stub: returns mock data when bridge is unavailable
        d = self.doctor()
        if not d.get("ok"):
            return d
        return self._unsupported("sensor_snapshot")
