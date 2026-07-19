"""Tests for pause/step simulation tools."""

from gazebo_mcp.backend.mock_sim import (
    mock_pause_simulation,
    mock_step_simulation,
    mock_resume_simulation,
)


def test_pause():
    result = mock_pause_simulation()
    assert result["ok"] is True
    assert result["paused"] is True


def test_step():
    result = mock_step_simulation(steps=10)
    assert result["ok"] is True
    assert result["paused"] is False
    assert result["steps_executed"] == 10
    assert result["sim_time"] == 0.01


def test_step_default():
    result = mock_step_simulation()
    assert result["steps_executed"] == 1
    assert result["sim_time"] == 0.001


def test_step_clamped():
    result = mock_step_simulation(steps=99999)
    assert result["steps_executed"] == 1000


def test_resume():
    result = mock_resume_simulation()
    assert result["ok"] is True
    assert result["paused"] is False
