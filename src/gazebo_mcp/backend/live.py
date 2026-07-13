"""Optional live Gazebo bridge (HTTP/file). Fails closed when unavailable."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from gazebo_mcp.config import bridge_file, bridge_url


class LiveBackend:
    name = "live"

    def doctor(self) -> dict[str, Any]:
        url = bridge_url()
        path = bridge_file()
        if url:
            try:
                with urlopen(Request(url.rstrip("/") + "/health", method="GET"), timeout=2) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                return {
                    "ok": True,
                    "connected": True,
                    "mode": "live",
                    "bridge": "http",
                    "health": body[:500],
                }
            except (URLError, TimeoutError, OSError) as exc:
                return {"ok": False, "connected": False, "mode": "live", "error": str(exc)}
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
        return self._unsupported("world_info")

    def list_models(self) -> list[dict[str, Any]]:
        return []

    def spawn(self, name: str, model_type: str, x: float, y: float, z: float, yaw: float = 0.0) -> dict[str, Any]:
        return self._unsupported("spawn")

    def delete(self, name: str) -> dict[str, Any]:
        return self._unsupported("delete")

    def get_pose(self, name: str) -> dict[str, Any]:
        return self._unsupported("get_pose")

    def set_pose(self, name: str, x: float, y: float, z: float, yaw: float = 0.0) -> dict[str, Any]:
        return self._unsupported("set_pose")

    def pause(self) -> dict[str, Any]:
        return self._unsupported("pause")

    def unpause(self) -> dict[str, Any]:
        return self._unsupported("unpause")

    def step(self, steps: int = 1) -> dict[str, Any]:
        return self._unsupported("step")
