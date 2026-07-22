"""Tests for gazebo_sensor_snapshot tool (#23, 100 MRG)."""
from gazebo_mcp.backend.mock import MockBackend


def test_sensor_lidar():
    b = MockBackend()
    result = b.sensor_snapshot("lidar", 1)
    assert len(result["frames"]) == 1
    frame = result["frames"][0]
    assert frame["type"] == "lidar_scan"
    assert len(frame["ranges"]) == 360
    assert frame["frame_status"] == "ok"


def test_sensor_camera():
    b = MockBackend()
    result = b.sensor_snapshot("camera", 1)
    assert len(result["frames"]) == 1
    frame = result["frames"][0]
    assert frame["type"] == "image_frame"
    assert frame["width"] == 640
    assert "K" in frame["camera_info"]


def test_sensor_depth():
    b = MockBackend()
    result = b.sensor_snapshot("depth", 1)
    assert len(result["frames"]) == 1
    assert result["frames"][0]["type"] == "depth_frame"
    assert result["frames"][0]["min_range"] == 0.1


def test_sensor_thermal():
    b = MockBackend()
    result = b.sensor_snapshot("thermal", 1)
    assert len(result["frames"]) == 1
    assert result["frames"][0]["type"] == "thermal_frame"
    assert result["frames"][0]["width"] == 320


def test_multi_frame():
    b = MockBackend()
    result = b.sensor_snapshot("lidar", 3)
    assert len(result["frames"]) == 3


def test_deterministic():
    b1 = MockBackend()
    r1 = b1.sensor_snapshot("lidar", 1)
    b2 = MockBackend()
    r2 = b2.sensor_snapshot("lidar", 1)
    assert r1["frames"][0]["ranges"] == r2["frames"][0]["ranges"]
