class MockEntityManager:
    # ... existing code ...

    @staticmethod
    def get_pose(entity_id):
        """Get the pose of a mock entity."""
        if entity_id not in MockEntityManager.entities:
            raise ValueError(f"Entity {entity_id} not found")

        return MockEntityManager.entities[entity_id].get('pose', {})

    @staticmethod
    def set_pose(entity_id, pose_data):
        """Set the pose of a mock entity."""
        if entity_id not in MockEntityManager.entities:
            raise ValueError(f"Entity {entity_id} not found")

        if not isinstance(pose_data, dict):
            raise ValueError("Pose data must be a dictionary")

        MockEntityManager.entities[entity_id]['pose'] = pose_data