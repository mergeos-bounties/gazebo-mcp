import unittest
from src.event_handler import EventHandler

class TestEventHandler(unittest.TestCase):
    def setUp(self):
        self.event_handler = EventHandler()
        self.captured_event = None

    def test_register_and_handle_event(self):
        def test_handler(event_data):
            self.captured_event = event_data

        self.event_handler.register_handler("test_event", test_handler)
        self.event_handler.handle_event("test_event", {"key": "value"})
        self.assertEqual(self.captured_event, {"key": "value"})

if __name__ == '__main__':
    unittest.main()