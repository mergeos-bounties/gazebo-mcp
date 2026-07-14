# gazebo-mcp

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-0E8A16.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-5319E7.svg)](https://modelcontextprotocol.io)
[![MergeOS](https://img.shields.io/badge/MergeOS-bounties-5319E7.svg)](https://github.com/mergeos-bounties)

**gazebo-mcp** is an [MCP](https://modelcontextprotocol.io) server so AI agents can drive **Gazebo / gz-sim**: worlds, models, poses, pause/step — with a full **offline mock** for CI and demos (no Gazebo install required).

**Product:** [mergeos-bounties/gazebo-mcp](https://github.com/mergeos-bounties/gazebo-mcp)

---

## Install (one command)

### Grok — recommended

```bash
pip install "git+https://github.com/mergeos-bounties/gazebo-mcp.git" && grok plugin install mergeos-bounties/gazebo-mcp --trust
```

This installs the **Python CLI** (`gazebo-mcp`) and the **Grok plugin** (skill + MCP server from `.mcp.json`).

Check:

```bash
gazebo-mcp version
gazebo-mcp doctor
gazebo-mcp demo
grok plugin list
grok mcp list
```

Local clone:

```bash
git clone https://github.com/mergeos-bounties/gazebo-mcp.git
cd gazebo-mcp
pip install -e ".[dev]"
grok plugin install . --trust
```

### Other agents (stdio MCP)

After `pip install "git+https://github.com/mergeos-bounties/gazebo-mcp.git"`, point any MCP host at:

| Field | Value |
| --- | --- |
| command | `gazebo-mcp` |
| args | `["serve"]` |
| env | `GAZEBO_MCP_MODE=mock` |

**Claude Desktop** — merge [examples/claude_desktop_config.json](examples/claude_desktop_config.json) into Claude MCP config.

**Cursor** — merge [examples/cursor_mcp.json](examples/cursor_mcp.json).

**Grok config.toml** (manual, without plugin):

```toml
[mcp_servers.gazebo_mcp]
command = "gazebo-mcp"
args = ["serve"]
env = { GAZEBO_MCP_MODE = "mock" }
enabled = true
```

**One-liner via Grok CLI:**

```bash
pip install "git+https://github.com/mergeos-bounties/gazebo-mcp.git"
grok mcp add gazebo-mcp -- gazebo-mcp serve
```


## Supported AI agents / hosts

| Host | Support | Install |
| --- | --- | --- |
| **Grok** (CLI / TUI / Build) | **Yes** | `grok plugin install mergeos-bounties/gazebo-mcp --trust` then `pip install "git+https://github.com/mergeos-bounties/gazebo-mcp.git"` |
| **Claude Desktop** | **Yes** | Copy [examples/claude_desktop_config.json](examples/claude_desktop_config.json) into Claude MCP settings |
| **Cursor** | **Yes** | Merge [examples/cursor_mcp.json](examples/cursor_mcp.json) into Cursor MCP config |
| **Claude Code** | **Yes** | stdio MCP: same `command`/`args` as Claude Desktop / Grok |
| **VS Code** (MCP / Continue / Cline) | **Yes** | Generic stdio server config pointing at `gazebo-mcp serve` |
| **Windsurf / Cascade** | **Yes** | stdio MCP entry with `gazebo-mcp` + `serve` |
| **Codex CLI** | **Yes** (stdio) | Register MCP server command `gazebo-mcp serve` in Codex MCP settings |
| **ChatGPT Desktop** | **Partial** | Only if host supports custom MCP stdio servers |
| **Gemini CLI** | **Partial** | Only if MCP stdio plugins are enabled |

All packages speak **MCP over stdio** (`gazebo-mcp serve`). Default mode is **mock** (offline, no simulator/terminal/GIMP required).


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
gazebo-mcp demo --profile fleet
gazebo-mcp doctor
pytest -q
```

```powershell
gazebo-mcp serve
```

---

## Docker mock image

Build a slim container that runs the MCP server in offline mock mode:

```powershell
docker build -t gazebo-mcp:mock .
```

Run the server over stdio:

```powershell
docker run --rm -i -e GAZEBO_MCP_MODE=mock gazebo-mcp:mock
```

Use Docker Compose for host integrations that expect a long-running stdio process:

```powershell
docker compose up --build gazebo-mcp
```

Offline smoke check without privileged host Gazebo:

```powershell
docker run --rm -e GAZEBO_MCP_MODE=mock gazebo-mcp:mock gazebo-mcp demo
```

The image installs only the Python package and its dependencies. It does not
install Gazebo, mount host devices, or require privileged container settings.

---

## Modes

| Mode | Env | Behavior |
| --- | --- | --- |
| **mock** (default) | `GAZEBO_MCP_MODE=mock` | In-memory world graph |
| **live** | `GAZEBO_MCP_MODE=live` + bridge URL/file | Forwards to local Gazebo bridge |

Live mode can restrict spawn model types before reaching the bridge:

```powershell
$env:GAZEBO_MCP_SPAWN_ALLOWLIST = "box,sphere,cylinder"
```

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

## Velocity metadata

Mock pose updates can store linear and angular velocity metadata alongside the
pose. The metadata is returned by `gazebo_get_pose`, `gazebo_list_models`, and
`gazebo://world` snapshots:

```powershell
gazebo-mcp call set_pose name=box_1 x=1 y=2 z=0.5 yaw=0.25 linear_x=0.2 angular_z=0.1
```

---

## Demo profiles

The default mock seed includes a ground plane, box, and sphere. The fleet
profile seeds `ground_plane` plus `robot_0`, `robot_1`, and `robot_2` with
distinct poses for multi-robot demos:

```powershell
gazebo-mcp demo --profile fleet
```

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

One-shot calls can read tool arguments from a JSON object file:

```json
{
  "name": "json_box",
  "model_type": "box",
  "x": 2,
  "y": 3,
  "z": 0.5
}
```

```powershell
gazebo-mcp call spawn --json-file args.json
```

---

## Examples

- [examples/cursor_mcp.json](examples/cursor_mcp.json)
- [examples/claude_desktop_config.json](examples/claude_desktop_config.json)
- [docs/HOST_SETUP.md](docs/HOST_SETUP.md) for Cursor, Claude Desktop, and Grok setup
- [docs/LIVE_BRIDGE.md](docs/LIVE_BRIDGE.md) for the live bridge health/world_info contract

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
