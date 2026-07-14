---
name: gazebo-mcp
description: >
  Gazebo / gz-sim worlds, models, poses (mock + live bridge). CLI `gazebo-mcp` + MCP stdio serve. Use when the user mentions
  gazebo-mcp, /gazebo-mcp, or related domain work. One-command Grok install from GitHub.
metadata:
  short-description: "Gazebo / gz-sim worlds, models, poses (mock + live bridge)."
---

# gazebo-mcp

## One-command install (Grok)

```bash
pip install "git+https://github.com/mergeos-bounties/gazebo-mcp.git" && grok plugin install mergeos-bounties/gazebo-mcp --trust
```

Or plugin first, then package:

```bash
grok plugin install mergeos-bounties/gazebo-mcp --trust
pip install "git+https://github.com/mergeos-bounties/gazebo-mcp.git"
```

Verify:

```bash
gazebo-mcp version
gazebo-mcp doctor
gazebo-mcp demo
gazebo-mcp serve   # MCP stdio for hosts
```

## Modes

| Env | Values |
| --- | --- |
| `GAZEBO_MCP_MODE` | `mock` (default) · `live` |

## MCP

```bash
gazebo-mcp serve
```

Config ships in plugin `.mcp.json`. Manual: see repo `examples/`.
