from __future__ import annotations

import json

from gazebo_mcp import server as srv
from gazebo_mcp.backend.mock import MockBackend
from gazebo_mcp.config import set_mode


def test_mock_snapshot_shape():
    b = MockBackend()
    snap = b.snapshot()
    assert snap["ok"] is True
    assert snap["world"] == "shapes_demo"
    assert snap["model_count"] == len(snap["models"]) == 3
    assert any(m["name"] == "box_1" for m in snap["models"])
    assert "sim_time_sec" in snap
    assert snap["physics"]["engine"] == "ode-mock"
    assert snap["physics"]["gravity"]["z"] == -9.8


def test_snapshot_reflects_spawn():
    b = MockBackend()
    b.spawn("cyl_1", "cylinder", 3.0, 0.0, 0.5)
    snap = b.snapshot()
    assert snap["model_count"] == 4
    assert any(m["name"] == "cyl_1" for m in snap["models"])


def test_world_resource_registered_and_returns_json():
    set_mode("mock")
    # resource callable is exposed on the module
    assert callable(srv.world_snapshot)
    payload = srv.world_snapshot()
    data = json.loads(payload)
    assert data["ok"] is True
    assert data["world"] == "shapes_demo"
    assert isinstance(data["models"], list)


def test_world_resource_registered_with_mcp():
    # confirm the gazebo://world resource is registered on the FastMCP server
    import asyncio

    resources = asyncio.run(srv.mcp.list_resources())
    uris = {str(r.uri) for r in resources}
    assert "gazebo://world" in uris
