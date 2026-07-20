import numpy as np
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SensorFrame:
    """Base class for sensor frames"""
    timestamp: float
    sensor_type: str

@dataclass
class LidarFrame(SensorFrame):
    """Lidar sensor frame data"""
    points: np.ndarray  # shape (N, 3) for x,y,z coordinates
    intensities: Optional[np.ndarray] = None  # shape (N,) for intensity values

@dataclass
class CameraFrame(SensorFrame):
    """Camera sensor frame data"""
    image: np.ndarray  # shape (H, W, 3) for RGB image
    depth: Optional[np.ndarray] = None  # shape (H, W) for depth values

class SensorSnapshot:
    """Tool for generating synthetic sensor frames"""

    def __init__(self):
        self.sensor_configs = {}

    def generate_lidar_frame(self, sensor_id: str, timestamp: float) -> LidarFrame:
        """Generate synthetic lidar frame"""
        # Simple mock implementation - replace with actual synthetic data generation
        num_points = 1000
        points = np.random.rand(num_points, 3) * 10  # Random points in 10x10x10 cube
        intensities = np.random.rand(num_points)  # Random intensities

        return LidarFrame(
            timestamp=timestamp,
            sensor_type="lidar",
            points=points,
            intensities=intensities
        )

    def generate_camera_frame(self, sensor_id: str, timestamp: float) -> CameraFrame:
        """Generate synthetic camera frame"""
        # Simple mock implementation - replace with actual synthetic data generation
        height, width = 480, 640
        image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        depth = np.random.rand(height, width) * 10  # Random depth values

        return CameraFrame(
            timestamp=timestamp,
            sensor_type="camera",
            image=image,
            depth=depth
        )

    def get_sensor_frame(self, sensor_id: str, timestamp: float) -> SensorFrame:
        """Get synthetic frame for specified sensor"""
        if sensor_id not in self.sensor_configs:
            raise ValueError(f"Sensor {sensor_id} not configured")

        sensor_type = self.sensor_configs[sensor_id]["type"]

        if sensor_type == "lidar":
            return self.generate_lidar_frame(sensor_id, timestamp)
        elif sensor_type == "camera":
            return self.generate_camera_frame(sensor_id, timestamp)
        else:
            raise ValueError(f"Unsupported sensor type: {sensor_type}")

    def configure_sensor(self, sensor_id: str, config: Dict[str, Any]) -> None:
        """Configure sensor parameters"""
        self.sensor_configs[sensor_id] = config