"""Tests for mock model lifecycle tools."""

from gazebo_mcp.backend.mock_model import (
    mock_spawn_model,
    mock_delete_model,
    mock_list_models,
    mock_reset_world,
)


def test_spawn_new_model():
    mock_reset_world()
    result = mock_spawn_model("cyl_1", "cylinder", 2.0, 1.0, 0.5, 1.57)
    assert result["ok"] is True
    assert result["model"]["name"] == "cyl_1"
    assert result["model"]["type"] == "cylinder"
    assert result["model"]["pose"]["x"] == 2.0
    assert result["model"]["pose"]["yaw"] == 1.57
    assert result["graph_version"] > 0


def test_spawn_duplicate_rejected():
    mock_reset_world()
    mock_spawn_model("dup_box", "box", 0, 0, 0.5)
    result = mock_spawn_model("dup_box", "box", 1, 1, 0.5)
    assert result["ok"] is False
    assert "already exists" in result["error"]


def test_spawn_invalid_type_rejected():
    mock_reset_world()
    result = mock_spawn_model("bad", "dinosaur", 0, 0, 0.5)
    assert result["ok"] is False
    assert "not in allowed set" in result["error"]
    assert "allowed_types" in result


def test_delete_existing_model():
    mock_reset_world()
    before = mock_list_models()
    assert any(m["name"] == "box_1" for m in before["models"])

    result = mock_delete_model("box_1")
    assert result["ok"] is True
    assert result["deleted"] == "box_1"
    assert result["was_type"] == "box"

    after = mock_list_models()
    assert not any(m["name"] == "box_1" for m in after["models"])
    assert after["model_count"] == before["model_count"] - 1


def test_delete_unknown_model():
    mock_reset_world()
    result = mock_delete_model("nonexistent")
    assert result["ok"] is False
    assert "unknown model" in result["error"]


def test_delete_ground_plane_rejected():
    mock_reset_world()
    result = mock_delete_model("ground_plane")
    assert result["ok"] is False
    assert "cannot delete" in result["error"]


def test_state_consistent_across_spawn_and_delete():
    """The acceptance criteria: state consistent across tools."""
    mock_reset_world()

    # spawn three models
    for i in range(3):
        result = mock_spawn_model(f"test_{i}", "box", float(i), 0.0, 0.5)
        assert result["ok"] is True

    # list must reflect all spawns
    listing = mock_list_models()
    names = {m["name"] for m in listing["models"]}
    for i in range(3):
        assert f"test_{i}" in names
    # defaults still present
    assert "ground_plane" in names
    assert "box_1" in names

    # delete one
    mock_delete_model("test_1")

    # state consistent after delete
    listing2 = mock_list_models()
    names2 = {m["name"] for m in listing2["models"]}
    assert "test_0" in names2
    assert "test_1" not in names2
    assert "test_2" in names2
    assert "ground_plane" in names2


def test_graph_version_monotonic():
    mock_reset_world()
    v0 = mock_list_models()["graph_version"]
    v1 = mock_spawn_model("mono_1", "sphere", 0, 0, 0.5)["graph_version"]
    v2 = mock_spawn_model("mono_2", "box", 1, 0, 0.5)["graph_version"]
    v3 = mock_delete_model("mono_1")["graph_version"]

    assert v0 < v1 < v2 < v3


def test_reset_world_clears_custom_models():
    mock_spawn_model("custom", "urdf", 5, 5, 1.0)
    assert mock_list_models()["model_count"] > 3

    mock_reset_world()
    listing = mock_list_models()
    names = {m["name"] for m in listing["models"]}
    assert "custom" not in names
    assert names == {"ground_plane", "box_1", "sphere_1"}
    assert listing["model_count"] == 3