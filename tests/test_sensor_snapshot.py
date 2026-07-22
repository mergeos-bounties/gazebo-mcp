"""Tests for sensor snapshot tools."""

from __future__ import annotations

from gazebo_mcp.backend.mock import MockBackend


def test_list_sensors():
    b = MockBackend()
    r = b.list_sensors()
    assert r["ok"]
    assert r["sensor_count"] >= 1
    names = {s["name"] for s in r["sensors"]}
    assert "front_camera" in names
    assert "lidar_top" in names


def test_camera_snapshot():
    b = MockBackend()
    r = b.sensor_snapshot("front_camera")
    assert r["ok"], r
    assert r["type"] == "camera"
    assert r["format"] == "rgb8"
    assert r["width"] == 640
    assert r["height"] == 480
    assert "mock_data_hash" in r


def test_camera_custom_resolution():
    b = MockBackend()
    r = b.sensor_snapshot("front_camera", resolution="1280x720")
    assert r["ok"], r
    assert r["width"] == 1280
    assert r["height"] == 720


def test_camera_bad_resolution_fallback():
    b = MockBackend()
    r = b.sensor_snapshot("front_camera", resolution="abc")
    assert r["ok"], r
    assert r["width"] == 640  # fallback default


def test_lidar_scan():
    b = MockBackend()
    r = b.sensor_snapshot("lidar_top")
    assert r["ok"], r
    assert r["type"] == "lidar"
    assert r["point_count"] == 360
    assert "ranges" in r


def test_imu_data():
    b = MockBackend()
    r = b.sensor_snapshot("imu_body")
    assert r["ok"], r
    assert r["type"] == "imu"
    assert "orientation" in r
    assert "linear_acceleration" in r


def test_unknown_sensor():
    b = MockBackend()
    r = b.sensor_snapshot("no_such_sensor")
    assert not r["ok"]


def test_snapshot_all():
    b = MockBackend()
    r = b.sensor_snapshot_all()
    assert r["ok"], r
    assert r["sensor_count"] == 3


def test_snapshot_all_filtered():
    b = MockBackend()
    r = b.sensor_snapshot_all(sensor_types="camera,lidar")
    assert r["ok"], r
    assert r["sensor_count"] == 2
    names = set(r["frames"])
    assert "front_camera" in names
    assert "imu_body" not in names


def test_sensor_still_present_after_seed():
    """Sensor state survives seed_demo."""
    b = MockBackend()
    b.seed_demo()
    r = b.list_sensors()
    assert r["sensor_count"] == 3