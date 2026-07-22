from gazebo_mcp.backend import get_backend
from gazebo_mcp.backend.mock import MockBackend
from gazebo_mcp.config import set_mode


def test_seed_and_models():
    b = MockBackend()
    s = b.seed_demo()
    assert s["ok"] is True
    assert s["profile"] == "default"
    models = b.list_models()
    assert any(m["name"] == "box_1" for m in models)
    assert b.doctor()["ok"] is True


def test_world_list_marks_active_fixture():
    b = MockBackend()
    worlds = b.list_worlds()

    assert worlds["ok"] is True
    assert worlds["current_world"] == "shapes_demo"
    assert {world["name"] for world in worlds["worlds"]} == {
        "shapes_demo",
        "fleet_demo",
    }
    assert next(world for world in worlds["worlds"] if world["active"])["name"] == "shapes_demo"

    b.seed_demo(profile="fleet")
    fleet = b.list_worlds()
    assert fleet["current_world"] == "fleet_demo"
    assert next(world for world in fleet["worlds"] if world["active"])["profile"] == "fleet"


def test_fleet_seed_profile():
    b = MockBackend()
    s = b.seed_demo(profile="fleet")
    assert s["ok"] is True
    assert s["profile"] == "fleet"
    models = b.list_models()
    names = {m["name"] for m in models}
    assert {"ground_plane", "robot_0", "robot_1", "robot_2"}.issubset(names)
    poses = [next(m for m in models if m["name"] == f"robot_{i}")["pose"] for i in range(3)]
    assert len({(p["x"], p["y"], p["yaw"]) for p in poses}) == 3
    assert all(next(m for m in models if m["name"] == f"robot_{i}")["type"] == "robot" for i in range(3))
    assert b.world_info()["world"] == "fleet_demo"


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


def test_spawn_state_consistency_across_tools():
    """Issue #19: Verify graph/list/world_info/snapshot stay consistent after spawn."""
    b = MockBackend()
    b.seed_demo()

    # Initial state: 3 models (ground_plane, box_1, sphere_1)
    assert b.world_info()["model_count"] == 3
    assert len(b.list_models()) == 3
    assert b.graph()["node_count"] == 3
    assert b.snapshot()["model_count"] == 3
    assert b.doctor()["model_count"] == 3

    # Spawn a new model
    result = b.spawn("cylinder_1", "cylinder", 0.5, 0.5, 0.3, 0.78)
    assert result["ok"] is True

    # Check all tools agree on model count = 4
    wi = b.world_info()
    assert wi["model_count"] == 4
    assert len(b.list_models()) == 4
    g = b.graph()
    assert g["node_count"] == 4
    assert b.snapshot()["model_count"] == 4
    assert b.doctor()["model_count"] == 4

    # Verify the new model appears in all views
    names_graph = {n["name"] for n in g["nodes"]}
    names_models = {m["name"] for m in b.list_models()}
    assert "cylinder_1" in names_graph
    assert "cylinder_1" in names_models
    assert names_graph == names_models  # full name consistency across graph/models

    # Verify parent-child in graph for new model
    cyl_node = next(n for n in g["nodes"] if n["name"] == "cylinder_1")
    assert cyl_node["parent"] == "ground_plane"
    assert "cylinder_1" in next(n for n in g["nodes"] if n["name"] == "ground_plane")["children"]

    # Snapshot contains the model
    snap_models = b.snapshot()["models"]
    snap_names = {m["name"] for m in snap_models}
    assert "cylinder_1" in snap_names


def test_delete_state_consistency_across_tools():
    """Issue #19: Verify graph/list/world_info/snapshot stay consistent after delete."""
    b = MockBackend()
    b.seed_demo()

    # Initial: 3 models
    assert b.world_info()["model_count"] == 3
    assert b.graph()["node_count"] == 3

    # Delete box_1
    result = b.delete("box_1")
    assert result["ok"] is True

    # Check all tools agree: 2 models
    assert b.world_info()["model_count"] == 2
    assert len(b.list_models()) == 2
    assert b.graph()["node_count"] == 2
    assert b.snapshot()["model_count"] == 2
    assert b.doctor()["model_count"] == 2

    # Verify box_1 is gone from all views
    names_graph = {n["name"] for n in b.graph()["nodes"]}
    names_models = {m["name"] for m in b.list_models()}
    assert "box_1" not in names_graph
    assert "box_1" not in names_models
    assert names_graph == names_models

    # ground_plane children should not include box_1
    ground_children = next(n for n in b.graph()["nodes"] if n["name"] == "ground_plane")["children"]
    assert "box_1" not in ground_children
    assert "sphere_1" in ground_children


def test_spawn_delete_spawn_cycle_consistent():
    """Issue #19: Chained operations keep all tools in sync."""
    b = MockBackend()
    b.seed_demo()

    def assert_state(expected_count):
        assert b.world_info()["model_count"] == expected_count
        assert len(b.list_models()) == expected_count
        assert b.graph()["node_count"] == expected_count
        assert b.snapshot()["model_count"] == expected_count
        assert b.doctor()["model_count"] == expected_count

    assert_state(3)

    b.spawn("a", "box", 1, 1, 1)
    assert_state(4)

    b.spawn("b", "sphere", 2, 2, 2)
    assert_state(5)

    b.delete("a")
    assert_state(4)

    b.delete("b")
    assert_state(3)

    b.spawn("c", "cylinder", 3, 3, 3)
    assert_state(4)

    # Verify all names match across tools
    g_names = {n["name"] for n in b.graph()["nodes"]}
    m_names = {m["name"] for m in b.list_models()}
    s_names = {m["name"] for m in b.snapshot()["models"]}
    assert g_names == m_names == s_names
    assert "c" in g_names
    assert "box_1" in g_names


def test_graph_and_snapshot_pose_match():
    """Issue #19: Graph pose matches model pose after spawn."""
    b = MockBackend()
    b.seed_demo()

    b.spawn("robot_x", "robot", 1.5, 2.5, 0.3, 0.9)

    # Graph should reflect spawn pose
    g = b.graph()
    robot_node = next(n for n in g["nodes"] if n["name"] == "robot_x")
    assert robot_node["pose"]["x"] == 1.5
    assert robot_node["pose"]["y"] == 2.5
    assert robot_node["pose"]["z"] == 0.3
    assert robot_node["pose"]["yaw"] == 0.9

    # Snapshot model list should match
    snap_robot = next(m for m in b.snapshot()["models"] if m["name"] == "robot_x")
    assert snap_robot["pose"]["x"] == 1.5
    assert snap_robot["pose"]["y"] == 2.5
    assert snap_robot["pose"]["z"] == 0.3
    assert snap_robot["pose"]["yaw"] == 0.9

    # list_models should match too
    list_robot = next(m for m in b.list_models() if m["name"] == "robot_x")
    assert list_robot["pose"]["x"] == 1.5
    assert list_robot["pose"]["y"] == 2.5
    assert list_robot["pose"]["z"] == 0.3
    assert list_robot["pose"]["yaw"] == 0.9