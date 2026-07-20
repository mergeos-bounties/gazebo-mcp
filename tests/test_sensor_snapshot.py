import unittest
import numpy as np
from skills.sensor_snapshot import SensorSnapshot, LidarFrame, CameraFrame

class TestSensorSnapshot(unittest.TestCase):
    def setUp(self):
        self.snapshot_tool = SensorSnapshot()
        self.snapshot_tool.configure_sensor("lidar1", {"type": "lidar"})
        self.snapshot_tool.configure_sensor("camera1", {"type": "camera"})

    def test_generate_lidar_frame(self):
        frame = self.snapshot_tool.generate_lidar_frame("lidar1", 12345.678)
        self.assertIsInstance(frame, LidarFrame)
        self.assertEqual(frame.timestamp, 12345.678)
        self.assertEqual(frame.sensor_type, "lidar")
        self.assertEqual(frame.points.shape[1], 3)  # Should have x,y,z coordinates
        if frame.intensities is not None:
            self.assertEqual(frame.intensities.shape[0], frame.points.shape[0])

    def test_generate_camera_frame(self):
        frame = self.snapshot_tool.generate_camera_frame("camera1", 12345.678)
        self.assertIsInstance(frame, CameraFrame)
        self.assertEqual(frame.timestamp, 12345.678)
        self.assertEqual(frame.sensor_type, "camera")
        self.assertEqual(frame.image.shape[2], 3)  # Should have RGB channels
        if frame.depth is not None:
            self.assertEqual(frame.depth.shape, frame.image.shape[:2])

    def test_get_sensor_frame(self):
        lidar_frame = self.snapshot_tool.get_sensor_frame("lidar1", 12345.678)
        self.assertIsInstance(lidar_frame, LidarFrame)

        camera_frame = self.snapshot_tool.get_sensor_frame("camera1", 12345.678)
        self.assertIsInstance(camera_frame, CameraFrame)

    def test_configure_sensor(self):
        self.snapshot_tool.configure_sensor("new_sensor", {"type": "lidar"})
        self.assertIn("new_sensor", self.snapshot_tool.sensor_configs)
        self.assertEqual(self.snapshot_tool.sensor_configs["new_sensor"]["type"], "lidar")

if __name__ == '__main__':
    unittest.main()