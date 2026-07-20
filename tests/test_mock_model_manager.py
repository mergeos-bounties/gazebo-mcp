import unittest
from src.mock_model_manager import MockModelManager
from src.state_manager import StateManager
from src.event_handler import EventHandler

class TestMockModelManager(unittest.TestCase):
    def setUp(self):
        self.state_manager = StateManager()
        self.event_handler = EventHandler()
        self.model_manager = MockModelManager(self.state_manager, self.event_handler)

    def test_spawn_model(self):
        model_data = {"type": "robot", "position": [0, 0, 0]}
        result = self.model_manager.spawn_model("test_model", model_data)
        self.assertTrue(result)
        self.assertIn("test_model", self.model_manager.mock_models)

    def test_delete_model(self):
        model_data = {"type": "robot", "position": [0, 0, 0]}
        self.model_manager.spawn_model("test_model", model_data)
        result = self.model_manager.delete_model("test_model")
        self.assertTrue(result)
        self.assertNotIn("test_model", self.model_manager.mock_models)

    def test_get_model(self):
        model_data = {"type": "robot", "position": [0, 0, 0]}
        self.model_manager.spawn_model("test_model", model_data)
        retrieved_model = self.model_manager.get_model("test_model")
        self.assertEqual(retrieved_model, model_data)

if __name__ == '__main__':
    unittest.main()