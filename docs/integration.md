# Gazebo Transport Integration

## Overview

This document describes the integration of Gazebo's gz transport system with the MCP server. The integration provides a real-time bridge between the MCP server and Gazebo simulations, allowing AI agents to interact with Gazebo worlds, models, and poses.

## Configuration

To use the Gazebo transport integration, set the `GAZEBO_MCP_BRIDGE_TYPE` environment variable to `gz`: