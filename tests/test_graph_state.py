"""Tests for mock backend graph state tracking."""

from gazebo_mcp.backend.mock import MockBackend


def test_graph_initial_state():
    b = MockBackend()
    g = b.graph()
    assert g["ok"] is True
    assert g["mode"] == "mock"
    assert g["world"] == "shapes_demo"
    assert g["node_count"] == 3  # ground_plane, box_1, sphere_1
    names = {n["name"] for n in g["nodes"]}
    assert names == {"ground_plane", "box_1", "sphere_1"}


def test_graph_parent_child_relationships():
    b = MockBackend()
    g = b.graph()
    ground = next(n for n in g["nodes"] if n["name"] == "ground_plane")
    assert ground["parent"] is None
    assert "box_1" in ground["children"]
    assert "sphere_1" in ground["children"]
    box = next(n for n in g["nodes"] if n["name"] == "box_1")
    assert box["parent"] == "ground_plane"


def test_graph_updates_after_spawn():
    b = MockBackend()
    b.spawn("robot_1", "robot", 1.0, 0.0, 0.1)
    g = b.graph()
    assert g["node_count"] == 4
    names = {n["name"] for n in g["nodes"]}
    assert "robot_1" in names
    robot = next(n for n in g["nodes"] if n["name"] == "robot_1")
    assert robot["parent"] == "ground_plane"
    assert robot["type"] == "robot"


def test_graph_updates_after_delete():
    b = MockBackend()
    b.delete("box_1")
    g = b.graph()
    assert g["node_count"] == 2
    names = {n["name"] for n in g["nodes"]}
    assert "box_1" not in names
    assert "sphere_1" in names


def test_graph_spawn_then_delete_consistent():
    b = MockBackend()
    b.spawn("test_cube", "box", 2.0, 2.0, 0.5)
    assert b.graph()["node_count"] == 4
    b.delete("test_cube")
    assert b.graph()["node_count"] == 3


def test_graph_fleet_profile():
    b = MockBackend()
    b.seed_demo(profile="fleet")
    g = b.graph()
    assert g["world"] == "fleet_demo"
    assert g["node_count"] == 4  # ground_plane + 3 robots
    names = {n["name"] for n in g["nodes"]}
    assert "robot_0" in names
    assert "robot_2" in names


def test_graph_pose_metadata():
    b = MockBackend()
    g = b.graph()
    box = next(n for n in g["nodes"] if n["name"] == "box_1")
    assert box["pose"]["x"] == 1.0
    assert box["pose"]["z"] == 0.5