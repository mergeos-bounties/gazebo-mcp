from gazebo_mcp.backend import get_backend
from gazebo_mcp.backend.mock import MockBackend
from gazebo_mcp.config import set_mode


def test_seed_and_models():
    b = MockBackend()
    s = b.seed_demo()
    assert s["ok"] is True
    models = b.list_models()
    assert any(m["name"] == "box_1" for m in models)
    assert b.doctor()["ok"] is True


def test_spawn_pose_step():
    b = MockBackend()
    b.seed_demo()
    sp = b.spawn("robot_1", "urdf", 0.0, 0.0, 0.1)
    assert sp["ok"] is True
    pose = b.set_pose("robot_1", 1.0, 2.0, 0.1, 0.5)
    assert pose["pose"]["x"] == 1.0
    st = b.step(5)
    assert st["steps"] == 5
    assert b.delete("robot_1")["ok"] is True


def test_set_pose_tracks_twist_metadata():
    b = MockBackend()
    b.seed_demo()
    result = b.set_pose(
        "box_1",
        1.0,
        2.0,
        0.5,
        0.25,
        linear_velocity={"x": 0.2, "y": 0.0, "z": 0.0},
        angular_velocity={"x": 0.0, "y": 0.0, "z": 0.1},
    )

    assert result["ok"] is True
    assert result["twist"]["linear"]["x"] == 0.2
    pose = b.get_pose("box_1")
    assert pose["twist"]["angular"]["z"] == 0.1
    box = next(m for m in b.list_models() if m["name"] == "box_1")
    assert box["twist"]["linear"]["x"] == 0.2


def test_get_backend_mock():
    set_mode("mock")
    assert get_backend().name == "mock"
