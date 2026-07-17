import json

from gazebo_mcp import server as srv


def test_tools_registered():
    assert callable(srv.gazebo_doctor)
    assert callable(srv.gazebo_spawn)
    assert callable(srv.gazebo_world_list)
    assert "mock" in srv.gazebo_mode()


def test_world_list_tool_returns_mock_fixtures():
    payload = json.loads(srv.gazebo_world_list())

    assert payload["ok"] is True
    assert payload["current_world"] == "shapes_demo"
    assert len(payload["worlds"]) == 2
