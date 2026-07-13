from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from gazebo_mcp.backend.live import LiveBackend


class BridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json({"ok": True, "service": "gazebo-bridge", "mode": "live"})
            return
        if self.path == "/world_info":
            self._json(
                {
                    "world": "default",
                    "paused": False,
                    "sim_time_sec": 12.5,
                    "model_count": 2,
                    "physics": "ode",
                }
            )
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _json(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_bridge() -> tuple[ThreadingHTTPServer, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), BridgeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, f"http://{host}:{port}"


def test_live_doctor_reads_health_json(monkeypatch):
    server, url = start_bridge()
    monkeypatch.setenv("GAZEBO_MCP_BRIDGE_URL", url)
    try:
        result = LiveBackend().doctor()
    finally:
        server.shutdown()
        server.server_close()

    assert result["ok"] is True
    assert result["connected"] is True
    assert result["bridge"] == "http"
    assert result["health"]["service"] == "gazebo-bridge"


def test_live_world_info_reads_json(monkeypatch):
    server, url = start_bridge()
    monkeypatch.setenv("GAZEBO_MCP_BRIDGE_URL", url)
    try:
        result = LiveBackend().world_info()
    finally:
        server.shutdown()
        server.server_close()

    assert result["ok"] is True
    assert result["world"] == "default"
    assert result["paused"] is False
    assert result["sim_time_sec"] == 12.5
    assert result["model_count"] == 2


def test_live_world_info_fails_closed_when_bridge_down(monkeypatch):
    server, url = start_bridge()
    server.shutdown()
    server.server_close()
    monkeypatch.setenv("GAZEBO_MCP_BRIDGE_URL", url)

    result = LiveBackend().world_info()

    assert result["ok"] is False
    assert result["connected"] is False
    assert result["mode"] == "live"
    assert "error" in result
