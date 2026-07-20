import unittest
from src.state_manager import StateManager

class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.state_manager = StateManager()

    def test_update_state(self):
        self.state_manager.update_state("test_key", "test_value")
        self.assertEqual(self.state_manager.get_state()["test_key"], "test_value")

    def test_mock_operation_state(self):
        self.state_manager.update_state("mock_operation")
        self.assertTrue(self.state_manager.get_state()["mock_operation"])

if __name__ == '__main__':
    unittest.main()