"""Tests for pose get/set tools - backend only (no server import)."""

from gazebo_mcp.backend.mock import MockBackend


def test_get_pose_returns_correct_pose():
    b = MockBackend()
    b.seed_demo()
    pose = b.get_pose("box_1")
    assert pose["ok"] is True
    assert pose["name"] == "box_1"
    assert pose["pose"]["x"] == 1.0
    assert pose["pose"]["y"] == 0.0
    assert pose["pose"]["z"] == 0.5
    assert pose["pose"]["yaw"] == 0.0


def test_get_pose_unknown_model():
    b = MockBackend()
    result = b.get_pose("nonexistent")
    assert result["ok"] is False
    assert "unknown" in result["error"]


def test_get_pose_returns_twist():
    b = MockBackend()
    b.seed_demo()
    pose = b.get_pose("box_1")
    assert "twist" in pose
    assert "linear" in pose["twist"]
    assert "angular" in pose["twist"]
    assert pose["twist"]["linear"]["x"] == 0.0


def test_set_pose_updates_position():
    b = MockBackend()
    b.seed_demo()
    result = b.set_pose("box_1", 5.0, 3.0, 2.0, 1.57)
    assert result["ok"] is True
    assert result["pose"]["x"] == 5.0
    assert result["pose"]["y"] == 3.0
    assert result["pose"]["z"] == 2.0
    assert result["pose"]["yaw"] == 1.57

    # Verify via get_pose
    readback = b.get_pose("box_1")
    assert readback["pose"]["x"] == 5.0


def test_set_pose_unknown_model():
    b = MockBackend()
    result = b.set_pose("ghost", 0.0, 0.0, 0.0)
    assert result["ok"] is False
    assert "unknown" in result["error"]


def test_set_pose_twist_metadata():
    b = MockBackend()
    b.seed_demo()
    result = b.set_pose(
        "sphere_1",
        -1.0, 0.5, 0.5, 0.0,
        linear_velocity={"x": 0.5, "y": 0.0, "z": 0.0},
        angular_velocity={"x": 0.0, "y": 0.0, "z": 0.2},
    )
    assert result["ok"] is True
    assert result["twist"]["linear"]["x"] == 0.5
    assert result["twist"]["angular"]["z"] == 0.2


def test_set_pose_persists_in_model_list():
    b = MockBackend()
    b.seed_demo()
    b.set_pose("box_1", 7.0, 8.0, 0.5, 3.14)
    models = b.list_models()
    box = next(m for m in models if m["name"] == "box_1")
    assert box["pose"]["x"] == 7.0
    assert box["pose"]["y"] == 8.0


def test_set_pose_fleet_profile():
    b = MockBackend()
    b.seed_demo(profile="fleet")
    result = b.set_pose("robot_0", 10.0, 10.0, 0.1, 0.0)
    assert result["ok"] is True
    assert result["pose"]["x"] == 10.0
    assert result["pose"]["y"] == 10.0


def test_get_pose_fleet_profile():
    b = MockBackend()
    b.seed_demo(profile="fleet")
    pose = b.get_pose("robot_1")
    assert pose["ok"] is True
    assert pose["name"] == "robot_1"
    assert pose["pose"]["yaw"] == 1.57