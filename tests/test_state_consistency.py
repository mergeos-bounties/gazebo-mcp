"""State consistency tests across mock tools (bounty #19)."""

from gazebo_mcp.backend.mock import MockBackend


def test_spawn_delete_state_consistency():
    """Spawn then delete should restore original model count."""
    b = MockBackend()
    b.seed_demo()
    before = len(b.list_models())

    sp = b.spawn("ephemeral_1", "box", 1.0, 2.0, 0.0)
    assert sp["ok"] is True
    assert len(b.list_models()) == before + 1

    sp2 = b.spawn("ephemeral_2", "sphere", 3.0, 4.0, 0.0)
    assert sp2["ok"] is True
    assert len(b.list_models()) == before + 2

    del1 = b.delete("ephemeral_1")
    assert del1["ok"] is True
    assert len(b.list_models()) == before + 1

    del2 = b.delete("ephemeral_2")
    assert del2["ok"] is True
    assert len(b.list_models()) == before


def test_duplicate_spawn_rejected():
    """Spawning a model that already exists should fail."""
    b = MockBackend()
    b.seed_demo()
    sp = b.spawn("box_1", "box", 1.0, 2.0, 0.0)
    assert sp["ok"] is False
    assert "already exists" in sp["error"]


def test_delete_unknown_model():
    """Deleting a non-existent model should fail."""
    b = MockBackend()
    result = b.delete("nonexistent_model")
    assert result["ok"] is False
    assert "unknown" in result["error"]


def test_ground_plane_protected():
    """Ground plane should not be deletable."""
    b = MockBackend()
    result = b.delete("ground_plane")
    assert result["ok"] is False
    assert "cannot delete" in result["error"]


def test_spawn_then_pose_consistency():
    """Spawned model should be queryable via get_pose."""
    b = MockBackend()
    b.seed_demo()
    b.spawn("new_robot", "robot", 5.0, 5.0, 0.0)
    pose = b.get_pose("new_robot")
    assert pose["ok"] is True
    assert pose["pose"]["x"] == 5.0
    assert pose["pose"]["y"] == 5.0


def test_spawn_delete_pause_consistency():
    """Pause state should survive spawn/delete cycle."""
    b = MockBackend()
    b.seed_demo()
    b.pause()
    assert b.world_info()["paused"] is True

    b.spawn("temp", "box", 0.0, 0.0, 0.0)
    assert b.world_info()["paused"] is True

    b.delete("temp")
    assert b.world_info()["paused"] is True


def test_ground_plane_cannot_be_spawned():
    """Spawning with name "ground_plane" should fail because it already exists."""
    b = MockBackend()
    b.seed_demo()
    # It will create a new entry that shadows the original
    result = b.spawn("ground_plane", "box", 0.0, 0.0, 0.0)
    assert result["ok"] is False
    assert "already exists" in result["error"]
    # But ground_plane is still protected from deletion
    assert b.delete("ground_plane")["ok"] is False
    # But ground_plane is still protected from deletion
    assert b.delete("ground_plane")["ok"] is False