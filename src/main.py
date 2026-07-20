"""
Main entry point for the MCP server.
"""

import os
from src.config import Config
from src.bridge import MockBridge
from src.gazebo_transport.bridge import GazeboBridge

def main():
    """
    Main function for the MCP server.
    """
    config = Config()

    # Set bridge type based on environment variable
    bridge_type = os.getenv("GAZEBO_MCP_BRIDGE_TYPE", "mock")
    config.set("bridge.type", bridge_type)

    # Initialize the appropriate bridge
    if bridge_type == "gz":
        bridge = GazeboBridge(config.get("bridge.config"))
    else:
        bridge = MockBridge(config.get("bridge.config"))

    # Start the server with the selected bridge
    # Implement server startup logic here

if __name__ == "__main__":
    main()