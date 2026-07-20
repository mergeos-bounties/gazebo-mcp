"""Mock pause/step simulation tools for gazebo-mcp."""

from __future__ import annotations

from typing import Any


def mock_pause_simulation() -> dict[str, Any]:
    """Pause the mock Gazebo simulation."""
    return {
        "ok": True,
        "paused": True,
        "sim_time": 0.0,
        "message": "Simulation paused",
    }


def mock_step_simulation(steps: int = 1) -> dict[str, Any]:
    """Step the mock Gazebo simulation forward by N steps.

    Args:
        steps: Number of simulation steps to execute (default 1).

    Returns:
        Dictionary with step count and updated sim time.
    """
    steps = max(1, min(steps, 1000))
    dt = 0.001  # 1ms per step
    return {
        "ok": True,
        "paused": False,
        "steps_executed": steps,
        "sim_time": steps * dt,
        "message": f"Stepped {steps} steps ({steps * dt:.3f}s)",
    }


def mock_resume_simulation() -> dict[str, Any]:
    """Resume the mock Gazebo simulation from paused state."""
    return {
        "ok": True,
        "paused": False,
        "message": "Simulation resumed",
    }
