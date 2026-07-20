"""
Unit tests for the Gazebo transport integration.
"""

import unittest
from src.gazebo_transport.bridge import GazeboBridge
from src.gazebo_transport.transport import GazeboTransport

class TestGazeboTransport(unittest.TestCase):
    """
    Unit tests for the Gazebo transport integration.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        self.config = {
            "bridge": {
                "type": "gz",
                "config": {}
            }
        }

    def test_bridge_connect(self):
        """
        Test connecting to the Gazebo bridge.
        """
        bridge = GazeboBridge(self.config["bridge"]["config"])
        self.assertTrue(bridge.connect())

    def test_bridge_disconnect(self):
        """
        Test disconnecting from the Gazebo bridge.
        """
        bridge = GazeboBridge(self.config["bridge"]["config"])
        bridge.connect()
        self.assertTrue(bridge.disconnect())

    def test_bridge_send(self):
        """
        Test sending data through the Gazebo bridge.
        """
        bridge = GazeboBridge(self.config["bridge"]["config"])
        bridge.connect()
        self.assertTrue(bridge.send({"test": "data"}))

    def test_bridge_receive(self):
        """
        Test receiving data from the Gazebo bridge.
        """
        bridge = GazeboBridge(self.config["bridge"]["config"])
        bridge.connect()
        data = bridge.receive()
        self.assertIsInstance(data, dict)

    def test_transport_connect(self):
        """
        Test connecting to the Gazebo transport.
        """
        transport = GazeboTransport(self.config["bridge"]["config"])
        self.assertTrue(transport.connect())

    def test_transport_disconnect(self):
        """
        Test disconnecting from the Gazebo transport.
        """
        transport = GazeboTransport(self.config["bridge"]["config"])
        transport.connect()
        self.assertTrue(transport.disconnect())

    def test_transport_send(self):
        """
        Test sending data through the Gazebo transport.
        """
        transport = GazeboTransport(self.config["bridge"]["config"])
        transport.connect()
        self.assertTrue(transport.send({"test": "data"}))

    def test_transport_receive(self):
        """
        Test receiving data from the Gazebo transport.
        """
        transport = GazeboTransport(self.config["bridge"]["config"])
        transport.connect()
        data = transport.receive()
        self.assertIsInstance(data, dict)

if __name__ == "__main__":
    unittest.main()