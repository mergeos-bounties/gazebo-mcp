from typer.testing import CliRunner

from gazebo_mcp.cli import app

runner = CliRunner()


def test_demo_exits_zero():
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0
    assert "demo complete" in result.stdout


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
