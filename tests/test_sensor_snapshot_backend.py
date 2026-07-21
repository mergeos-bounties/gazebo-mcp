"""Tests for sensor snapshot tool - backend only (no server import)."""

from gazebo_mcp.backend.mock import MockBackend


def test_sensor_lidar_default():
    b = MockBackend()
    result = b.sensor_snapshot()
    assert result["ok"] is True
    assert result["sensor_type"] == "lidar"
    assert result["mode"] == "mock"
    assert "data" in result
    assert result["data"]["num_points"] == 360
    assert "points" in result["data"]
    assert len(result["data"]["points"]) == 36  # every 10 degrees


def test_sensor_camera():
    b = MockBackend()
    result = b.sensor_snapshot(sensor_type="camera")
    assert result["ok"] is True
    assert result["sensor_type"] == "camera"
    assert result["data"]["width"] == 640
    assert result["data"]["height"] == 480
    assert result["data"]["fov_deg"] == 90.0


def test_sensor_depth():
    b = MockBackend()
    result = b.sensor_snapshot(sensor_type="depth")
    assert result["ok"] is True
    assert result["sensor_type"] == "depth"
    assert result["data"]["width"] == 320
    assert result["data"]["range_max"] == 10.0


def test_sensor_imu():
    b = MockBackend()
    result = b.sensor_snapshot(sensor_type="imu")
    assert result["ok"] is True
    assert result["sensor_type"] == "imu"
    assert result["data"]["orientation"]["w"] == 1.0
    assert result["data"]["linear_acceleration"]["z"] == -9.8


def test_sensor_unknown_type():
    b = MockBackend()
    result = b.sensor_snapshot(sensor_type="sonar")
    assert result["ok"] is False
    assert "unsupported" in result["error"]


def test_sensor_with_model_name():
    b = MockBackend()
    result = b.sensor_snapshot(sensor_type="lidar", name="box_1")
    assert result["ok"] is True
    assert result["model"] == "box_1"
    assert result["pose"]["x"] == 1.0


def test_sensor_unknown_model():
    b = MockBackend()
    result = b.sensor_snapshot(sensor_type="camera", name="ghost")
    assert result["ok"] is False
    assert "unknown" in result["error"]


def test_sensor_in_fleet_world():
    b = MockBackend()
    b.seed_demo(profile="fleet")
    result = b.sensor_snapshot(sensor_type="lidar", name="robot_0")
    assert result["ok"] is True
    assert result["world"] == "fleet_demo"
    assert result["model"] == "robot_0"


def test_sensor_case_insensitive():
    b = MockBackend()
    result = b.sensor_snapshot(sensor_type="LIDAR")
    assert result["ok"] is True
    assert result["sensor_type"] == "lidar"

    result = b.sensor_snapshot(sensor_type="Camera")
    assert result["ok"] is True
    assert result["sensor_type"] == "camera"