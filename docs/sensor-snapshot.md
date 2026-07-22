# Sensor Snapshot Tool

## Overview
The `gazebo_sensor_snapshot` tool returns synthetic sensor frames for AI agent workflows.
Supports: **lidar**, **camera**, **depth**, **thermal**.

## Usage
```
gazebo_sensor_snapshot(sensor_type="lidar", count=1)
gazebo_sensor_snapshot(sensor_type="camera", count=3)
```

## Schemas

### LIDAR (`sensor_type="lidar"`)
| Field | Type | Description |
|-------|------|-------------|
| frame_id | string | Unique identifier |
| timestamp | float | Sim time (s) |
| type | string | "lidar_scan" |
| ranges | array[float] | 360 distance readings (0.5–10m) |
| angle_min/max | float | ±π rad |
| width | int | 360 |

### Camera (`sensor_type="camera"`)
| Field | Type | Description |
|-------|------|-------------|
| width/height | int | 640×480 |
| encoding | string | "rgb8" |
| camera_info.K | array[float] | 3×3 intrinsic matrix |
| pose | object | Position + quaternion orientation |

### Depth (`sensor_type="depth"`)
| Field | Type | Description |
|-------|------|-------------|
| width/height | int | 640×480 |
| encoding | string | "32FC1" |
| min/max_range | float | 0.1–30.0m |

### Thermal (`sensor_type="thermal"`)
| Field | Type | Description |
|-------|------|-------------|
| width/height | int | 320×240 |
| encoding | string | "mono16" |
| min/max_temp | float | -20°C to 100°C |
