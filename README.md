# gazebo-mcp

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-0E8A16.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-5319E7.svg)](https://modelcontextprotocol.io)
[![MergeOS](https://img.shields.io/badge/MergeOS-bounties-5319E7.svg)](https://github.com/mergeos-bounties)

**gazebo-mcp** is an [MCP](https://modelcontextprotocol.io) server so AI agents can drive **Gazebo / gz-sim**: worlds, models, poses, pause/step — with a full **offline mock** for CI and demos (no Gazebo install required).

**Product:** [mergeos-bounties/gazebo-mcp](https://github.com/mergeos-bounties/gazebo-mcp)

---

## Highlights

| Capability | Description |
| --- | --- |
| **Offline mock** | Seeded world + models; spawn/delete/pose without Gazebo |
| **Live bridge** | Optional HTTP/file bridge when `GAZEBO_MCP_MODE=live` |
| **MCP stdio** | Cursor / Claude / Grok host integration |
| **CLI** | `demo` · `doctor` · `serve` · `call` |

---

## Quick start

```powershell
cd gazebo-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
gazebo-mcp demo
gazebo-mcp doctor
pytest -q
```

```powershell
gazebo-mcp serve
```

---

## Modes

| Mode | Env | Behavior |
| --- | --- | --- |
| **mock** (default) | `GAZEBO_MCP_MODE=mock` | In-memory world graph |
| **live** | `GAZEBO_MCP_MODE=live` + bridge URL/file | Forwards to local Gazebo bridge |

---

## Tools

| Tool | Purpose |
| --- | --- |
| `gazebo_doctor` | Connectivity / sim health |
| `gazebo_seed_demo` | Reset mock shapes world |
| `gazebo_world_info` | World name, paused, sim time |
| `gazebo_list_models` | Models in the world |
| `gazebo_spawn` / `gazebo_delete` | Model lifecycle |
| `gazebo_set_pose` / `gazebo_get_pose` | Pose control |
| `gazebo_pause` / `gazebo_unpause` / `gazebo_step` | Clock control |

---

## Resources

| Resource URI | Purpose |
| --- | --- |
| `gazebo://world` | JSON snapshot of the current world: models + poses, sim time, paused state, physics params |

The `gazebo://world` resource returns the live mock world state (or the live-bridge
state in `live` mode). Example payload:

```json
{
  "ok": true,
  "world": "shapes_demo",
  "paused": false,
  "sim_time_sec": 1.234,
  "model_count": 3,
  "models": [
    {"name": "ground_plane", "type": "plane", "pose": {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}},
    {"name": "box_1", "type": "box", "pose": {"x": 1.0, "y": 0.0, "z": 0.5, "yaw": 0.0}},
    {"name": "sphere_1", "type": "sphere", "pose": {"x": -1.0, "y": 0.5, "z": 0.5, "yaw": 0.0}}
  ],
  "physics": {
    "engine": "ode-mock",
    "max_step_size": 0.001,
    "real_time_factor": 1.0,
    "gravity": {"x": 0.0, "y": 0.0, "z": -9.8}
  }
}
```

Smoke it offline via the CLI:

```powershell
gazebo-mcp call snapshot
```

---

## Examples

- [examples/cursor_mcp.json](examples/cursor_mcp.json)
- [examples/claude_desktop_config.json](examples/claude_desktop_config.json)
- [docs/HOST_SETUP.md](docs/HOST_SETUP.md) for Cursor, Claude Desktop, and Grok setup

---

## Development

```powershell
ruff check src tests
pytest -q
gazebo-mcp tools list
```

---

## MergeOS bounties

Star → claim issue → PR to **master** → MRG **25–200**.  
See [mergeos](https://github.com/mergeos-bounties/mergeos).

---

## License

MIT · MergeOS / ThanhTrucSolutions
