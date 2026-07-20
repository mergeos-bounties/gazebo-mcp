import gz.sim7 as gz

class LiveEntityManager:
    # ... existing code ...

    @staticmethod
    def get_pose(entity_id):
        """Get the pose of a live entity in Gazebo."""
        try:
            entity = gz.sim7.Entity(entity_id)
            if not entity.valid():
                raise ValueError(f"Entity {entity_id} not found")

            pose = entity.world_pose()
            return {
                'position': {
                    'x': pose.position.x,
                    'y': pose.position.y,
                    'z': pose.position.z
                },
                'orientation': {
                    'x': pose.orientation.x,
                    'y': pose.orientation.y,
                    'z': pose.orientation.z,
                    'w': pose.orientation.w
                }
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get pose for entity {entity_id}: {str(e)}")

    @staticmethod
    def set_pose(entity_id, pose_data):
        """Set the pose of a live entity in Gazebo."""
        try:
            entity = gz.sim7.Entity(entity_id)
            if not entity.valid():
                raise ValueError(f"Entity {entity_id} not found")

            if not isinstance(pose_data, dict):
                raise ValueError("Pose data must be a dictionary")

            position = pose_data.get('position', {})
            orientation = pose_data.get('orientation', {})

            pose = gz.sim7.Pose(
                gz.sim7.Vector3D(
                    position.get('x', 0.0),
                    position.get('y', 0.0),
                    position.get('z', 0.0)
                ),
                gz.sim7.Quaternion(
                    orientation.get('x', 0.0),
                    orientation.get('y', 0.0),
                    orientation.get('z', 0.0),
                    orientation.get('w', 1.0)
                )
            )

            entity.set_world_pose(pose)
        except Exception as e:
            raise RuntimeError(f"Failed to set pose for entity {entity_id}: {str(e)}")