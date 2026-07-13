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


def test_call_accepts_json_file(tmp_path):
    args_file = tmp_path / "spawn.json"
    args_file.write_text(
        '{"name":"json_box","model_type":"box","x":2,"y":3,"z":0.5}',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["call", "spawn", "--json-file", str(args_file)])

    assert result.exit_code == 0
    assert "json_box" in result.stdout
    assert "'ok': True" in result.stdout


def test_call_accepts_json_file_with_utf8_bom(tmp_path):
    args_file = tmp_path / "spawn-bom.json"
    args_file.write_text(
        '{"name":"bom_box","model_type":"box","x":2,"y":3,"z":0.5}',
        encoding="utf-8-sig",
    )

    result = runner.invoke(app, ["call", "spawn", "--json-file", str(args_file)])

    assert result.exit_code == 0
    assert "bom_box" in result.stdout


def test_call_rejects_invalid_json_file(tmp_path):
    args_file = tmp_path / "bad.json"
    args_file.write_text("{not-json", encoding="utf-8")

    result = runner.invoke(app, ["call", "spawn", "--json-file", str(args_file)])

    assert result.exit_code != 0
    assert "invalid JSON" in result.stderr
