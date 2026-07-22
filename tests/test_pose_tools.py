"""Pose tool tests for get/set mock (bounty #20)."""

from gazebo_mcp.backend.mock import MockBackend


def test_get_pose_known_model():
    """Getting pose of existing model returns correct values."""
    b = MockBackend()
    b.seed_demo()
    result = b.get_pose("box_1")
    assert result["ok"] is True
    assert result["name"] == "box_1"
    assert "pose" in result
    assert "x" in result["pose"]
    assert "y" in result["pose"]
    assert "z" in result["pose"]
    assert "yaw" in result["pose"]


def test_get_pose_unknown_model():
    """Getting pose of non-existent model returns error."""
    b = MockBackend()
    result = b.get_pose("nonexistent")
    assert result["ok"] is False
    assert "unknown" in result["error"]


def test_set_pose_updates_all_axes():
    """Setting pose updates x, y, z, and yaw."""
    b = MockBackend()
    b.seed_demo()
    result = b.set_pose("box_1", 1.0, 2.0, 3.0, 0.5)
    assert result["ok"] is True
    assert result["pose"]["x"] == 1.0
    assert result["pose"]["y"] == 2.0
    assert result["pose"]["z"] == 3.0
    assert result["pose"]["yaw"] == 0.5


def test_set_pose_then_get_pose_consistency():
    """Set pose then get pose should return the same values."""
    b = MockBackend()
    b.seed_demo()
    b.set_pose("box_1", 10.0, 20.0, 30.0, 1.57)
    result = b.get_pose("box_1")
    assert result["pose"]["x"] == 10.0
    assert result["pose"]["y"] == 20.0
    assert result["pose"]["z"] == 30.0
    assert result["pose"]["yaw"] == 1.57


def test_set_pose_unknown_model():
    """Setting pose of non-existent model returns error."""
    b = MockBackend()
    result = b.set_pose("nonexistent", 0.0, 0.0, 0.0)
    assert result["ok"] is False
    assert "unknown" in result["error"]


def test_set_pose_negative_coordinates():
    """Negative coordinates should be accepted."""
    b = MockBackend()
    b.seed_demo()
    result = b.set_pose("box_1", -5.0, -10.0, -0.5, -1.57)
    assert result["ok"] is True
    assert result["pose"]["x"] == -5.0
    assert result["pose"]["y"] == -10.0


def test_get_pose_includes_twist():
    """Get pose should include twist metadata."""
    b = MockBackend()
    b.seed_demo()
    result = b.get_pose("box_1")
    assert "twist" in result
    assert "linear" in result["twist"]
    assert "angular" in result["twist"]
    assert "x" in result["twist"]["linear"]
    assert "z" in result["twist"]["angular"]
