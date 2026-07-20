import unittest
from unittest.mock import patch
from src.mock.mock_entity_manager import MockEntityManager
from src.live.live_entity_manager import LiveEntityManager

class TestPoseTools(unittest.TestCase):
    def setUp(self):
        # Initialize mock entities
        MockEntityManager.entities = {
            'test_entity': {
                'pose': {
                    'position': {'x': 1.0, 'y': 2.0, 'z': 3.0},
                    'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
                }
            }
        }

    def test_mock_get_pose(self):
        pose = MockEntityManager.get_pose('test_entity')
        self.assertEqual(pose['position']['x'], 1.0)
        self.assertEqual(pose['position']['y'], 2.0)
        self.assertEqual(pose['position']['z'], 3.0)

    def test_mock_set_pose(self):
        new_pose = {
            'position': {'x': 4.0, 'y': 5.0, 'z': 6.0},
            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
        }
        MockEntityManager.set_pose('test_entity', new_pose)
        updated_pose = MockEntityManager.get_pose('test_entity')
        self.assertEqual(updated_pose['position']['x'], 4.0)
        self.assertEqual(updated_pose['position']['y'], 5.0)
        self.assertEqual(updated_pose['position']['z'], 6.0)

    @patch('gz.sim7.Entity')
    def test_live_get_pose(self, mock_entity):
        mock_entity.return_value.valid.return_value = True
        mock_entity.return_value.world_pose.return_value.position.x = 1.0
        mock_entity.return_value.world_pose.return_value.position.y = 2.0
        mock_entity.return_value.world_pose.return_value.position.z = 3.0
        mock_entity.return_value.world_pose.return_value.orientation.x = 0.0
        mock_entity.return_value.world_pose.return_value.orientation.y = 0.0
        mock_entity.return_value.world_pose.return_value.orientation.z = 0.0
        mock_entity.return_value.world_pose.return_value.orientation.w = 1.0

        pose = LiveEntityManager.get_pose('test_entity')
        self.assertEqual(pose['position']['x'], 1.0)
        self.assertEqual(pose['position']['y'], 2.0)
        self.assertEqual(pose['position']['z'], 3.0)

    @patch('gz.sim7.Entity')
    def test_live_set_pose(self, mock_entity):
        mock_entity.return_value.valid.return_value = True
        mock_entity.return_value.set_world_pose.return_value = None

        new_pose = {
            'position': {'x': 4.0, 'y': 5.0, 'z': 6.0},
            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
        }
        LiveEntityManager.set_pose('test_entity', new_pose)
        mock_entity.return_value.set_world_pose.assert_called_once()