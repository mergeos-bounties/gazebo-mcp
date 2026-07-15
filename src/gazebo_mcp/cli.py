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
    info["tool_count"] = _count_tools()
    rprint(info)


def _count_tools() -> int:
    try:
        from gazebo_mcp.server import mcp
        tools = getattr(mcp, "_tool_manager", None)
        if tools:
            return len(getattr(tools, "_tools", {}) or {})
    except Exception:
        pass
    return 0


@app.command("quickstart")
def quickstart_cmd() -> None:
    """Print mock vs live quickstart guide."""
    console.print("[bold]gazebo-mcp Quickstart[/bold]\n")
    console.print("[cyan]Mock mode (offline, no Gazebo needed):[/cyan]")
    console.print("  gazebo-mcp demo")
    console.print("  gazebo-mcp doctor\n")
    console.print("[cyan]Live mode (requires Gazebo + gz-transport):[/cyan]")
    console.print("  export GAZEBO_MCP_MODE=live")
    console.print("  gazebo-mcp doctor")
    console.print("  gazebo-mcp demo --profile fleet\n")
    console.print("[dim]Mock mode supports world_list, model_spawn, pose_get/set, step_simulation[/dim]")
    console.print("[dim]Live mode bridges gz-transport for real simulation control[/dim]")


@app.command("demo")
def demo_cmd(
    profile: str = typer.Option("default", "--profile", help="Mock seed profile: default or fleet."),
) -> None:
    """Offline smoke: seed mock world, spawn, pose, step."""
    set_mode("mock")
    b = get_backend()
    rprint(b.seed_demo(profile=profile))
    rprint(b.doctor())
    rprint({"world": b.world_info()})
    rprint({"models": b.list_models()})
    if not any(m.get("name") == "cylinder_demo" for m in b.list_models()):
        rprint({"spawn": b.spawn("cylinder_demo", "cylinder", 2.0, 1.0, 0.5)})
    pose_target = "box_1" if any(m.get("name") == "box_1" for m in b.list_models()) else "robot_0"
    rprint({"pose": b.set_pose(pose_target, 1.5, 0.0, 0.5, 0.2)})
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
            _vec(kv, "linear"),
            _vec(kv, "angular"),
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


def _vec(kv: dict[str, Any], prefix: str) -> dict[str, float]:
    nested = kv.get(f"{prefix}_velocity")
    if isinstance(nested, dict):
        return {
            "x": float(nested.get("x", 0.0)),
            "y": float(nested.get("y", 0.0)),
            "z": float(nested.get("z", 0.0)),
        }
    return {
        "x": float(kv.get(f"{prefix}_x", 0.0)),
        "y": float(kv.get(f"{prefix}_y", 0.0)),
        "z": float(kv.get(f"{prefix}_z", 0.0)),
    }


@app.command("serve")
def serve_cmd() -> None:
    from gazebo_mcp.server import run_stdio

    run_stdio()


def main() -> None:
    app()


if __name__ == "__main__":
    app()
