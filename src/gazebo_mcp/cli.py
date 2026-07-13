from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from gazebo_mcp import __version__
from gazebo_mcp.backend import get_backend, switch_mode
from gazebo_mcp.config import get_mode, set_mode

app = typer.Typer(help="gazebo-mcp — MCP server for Gazebo / gz-sim", no_args_is_help=True)
tools_app = typer.Typer(help="List / probe tools")
app.add_typer(tools_app, name="tools")
console = Console()

TOOL_NAMES = [
    "gazebo_mode",
    "gazebo_doctor",
    "gazebo_seed_demo",
    "gazebo_world_info",
    "gazebo_list_models",
    "gazebo_spawn",
    "gazebo_delete",
    "gazebo_get_pose",
    "gazebo_set_pose",
    "gazebo_pause",
    "gazebo_unpause",
    "gazebo_step",
]


@app.command("version")
def version_cmd() -> None:
    rprint({"version": __version__, "mode": get_mode()})


@app.command("doctor")
def doctor_cmd() -> None:
    b = get_backend()
    info = b.doctor()
    info["gazebo_mcp_version"] = __version__
    info["mode"] = get_mode()
    rprint(info)


@app.command("demo")
def demo_cmd() -> None:
    """Offline smoke: seed mock world, spawn, pose, step."""
    set_mode("mock")
    b = get_backend()
    rprint(b.seed_demo())
    rprint(b.doctor())
    rprint({"world": b.world_info()})
    rprint({"models": b.list_models()})
    rprint({"spawn": b.spawn("cylinder_demo", "cylinder", 2.0, 1.0, 0.5)})
    rprint({"pose": b.set_pose("box_1", 1.5, 0.0, 0.5, 0.2)})
    rprint({"pause": b.pause()})
    rprint({"step": b.step(10)})
    rprint({"unpause": b.unpause()})
    rprint("gazebo-mcp demo complete (mock).")


@tools_app.command("list")
def tools_list() -> None:
    table = Table(title="gazebo-mcp tools")
    table.add_column("Tool")
    for n in TOOL_NAMES:
        table.add_row(n)
    console.print(table)


@app.command("call")
def call_cmd(
    tool: str = typer.Argument(..., help="Short name e.g. doctor or gazebo_doctor"),
    arg: Optional[list[str]] = typer.Argument(None, help="key=value pairs"),
    json_file: Optional[Path] = typer.Option(
        None,
        "--json-file",
        help="Read tool arguments from a JSON object file; key=value args override it.",
    ),
) -> None:
    b = get_backend()
    name = tool if tool.startswith("gazebo_") else f"gazebo_{tool}"
    kv: dict[str, Any] = _load_json_args(json_file) if json_file else {}
    for a in arg or []:
        if "=" in a:
            k, v = a.split("=", 1)
            try:
                kv[k] = json.loads(v)
            except json.JSONDecodeError:
                kv[k] = v
    dispatch = {
        "gazebo_mode": lambda: switch_mode(str(kv.get("mode", get_mode()))),
        "gazebo_doctor": b.doctor,
        "gazebo_seed_demo": b.seed_demo,
        "gazebo_world_info": b.world_info,
        "gazebo_list_models": b.list_models,
        "gazebo_snapshot": b.snapshot,
        "gazebo_spawn": lambda: b.spawn(
            str(kv.get("name", "obj")),
            str(kv.get("model_type", "box")),
            float(kv.get("x", 0)),
            float(kv.get("y", 0)),
            float(kv.get("z", 0.5)),
            float(kv.get("yaw", 0)),
        ),
        "gazebo_delete": lambda: b.delete(str(kv.get("name", ""))),
        "gazebo_get_pose": lambda: b.get_pose(str(kv.get("name", "box_1"))),
        "gazebo_set_pose": lambda: b.set_pose(
            str(kv.get("name", "box_1")),
            float(kv.get("x", 0)),
            float(kv.get("y", 0)),
            float(kv.get("z", 0.5)),
            float(kv.get("yaw", 0)),
        ),
        "gazebo_pause": b.pause,
        "gazebo_unpause": b.unpause,
        "gazebo_step": lambda: b.step(int(kv.get("steps", 1))),
    }
    if name not in dispatch:
        raise typer.BadParameter(f"unknown tool {name}")
    rprint(dispatch[name]())


def _load_json_args(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise typer.BadParameter(f"could not read JSON file {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise typer.BadParameter(f"JSON file {path} must contain an object")
    return data


@app.command("serve")
def serve_cmd() -> None:
    from gazebo_mcp.server import run_stdio

    run_stdio()


def main() -> None:
    app()


if __name__ == "__main__":
    app()
