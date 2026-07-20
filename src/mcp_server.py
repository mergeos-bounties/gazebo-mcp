# Add to existing imports
from skills.sensor_snapshot import SensorSnapshot

# Add to MCPServer class initialization
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.sensor_snapshot = SensorSnapshot()

# Add to MCPServer class methods
async def handle_sensor_snapshot(self, request: dict) -> dict:
    """Handle sensor snapshot requests"""
    try:
        sensor_id = request["sensor_id"]
        timestamp = request["timestamp"]

        frame = self.sensor_snapshot.get_sensor_frame(sensor_id, timestamp)

        # Convert numpy arrays to lists for JSON serialization
        if hasattr(frame, 'points'):
            frame.points = frame.points.tolist()
        if hasattr(frame, 'intensities') and frame.intensities is not None:
            frame.intensities = frame.intensities.tolist()
        if hasattr(frame, 'image'):
            frame.image = frame.image.tolist()
        if hasattr(frame, 'depth') and frame.depth is not None:
            frame.depth = frame.depth.tolist()

        return {
            "status": "success",
            "frame": frame.__dict__
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Add to MCPServer class method mappings
self.method_handlers = {
    # ... existing handlers ...
    "sensor_snapshot": self.handle_sensor_snapshot,
}