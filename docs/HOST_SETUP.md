# Host setup

This guide shows how to connect `gazebo-mcp` to MCP-capable hosts without
requiring a local Gazebo install. The default setup uses the offline mock backend
so the server can be tested in CI, on laptops, or in a fresh agent workspace.

## Prerequisites

Install the package in a Python 3.11+ environment:

```powershell
git clone https://github.com/mergeos-bounties/gazebo-mcp.git
cd gazebo-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Verify the server before wiring it into a host:

```powershell
gazebo-mcp demo
gazebo-mcp doctor
gazebo-mcp tools list
```

Expected demo evidence, shortened for readability:

```text
{'ok': True, 'world': 'shapes_demo', ...}
{'ok': True, 'mode': 'mock', ...}
gazebo-mcp demo complete (mock).
```

## Mode selection

`GAZEBO_MCP_MODE=mock` is the default and recommended first-run mode. It uses an
in-memory world graph and does not need Gazebo, gz-sim, ROS, or a bridge process.

Use `GAZEBO_MCP_MODE=live` only after you have a local Gazebo bridge configured.
Live mode should point to a trusted local bridge endpoint or file path. Do not
paste access tokens, cloud credentials, or private URLs into host config files.

## Cursor

Add the server to your Cursor MCP configuration. The exact settings location can
vary by Cursor version; use the MCP server JSON editor or the project/user MCP
configuration file that Cursor exposes.

Annotated JSON:

```json
{
  "mcpServers": {
    "gazebo-mcp": {
      "command": "gazebo-mcp",
      "args": ["serve"],
      "env": {
        "GAZEBO_MCP_MODE": "mock"
      }
    }
  }
}
```

After saving the config, restart or reload MCP servers in Cursor. A healthy
mock-mode connection should expose tools such as `gazebo_doctor`,
`gazebo_seed_demo`, `gazebo_world_info`, and `gazebo_list_models`.

## Claude Desktop

Open Claude Desktop's MCP configuration file and add the same server definition:

```json
{
  "mcpServers": {
    "gazebo-mcp": {
      "command": "gazebo-mcp",
      "args": ["serve"],
      "env": {
        "GAZEBO_MCP_MODE": "mock"
      }
    }
  }
}
```

Restart Claude Desktop after saving. In a new chat, ask Claude to inspect the
available Gazebo tools or run a mock world check. The host should start
`gazebo-mcp serve` over stdio and keep the interaction fully local.

## Grok

For Grok clients or wrappers that support MCP stdio servers, register the server
with the same command, args, and environment. If your Grok integration separates
command and environment fields in the UI, map the fields as shown here:

```json
{
  "mcpServers": {
    "gazebo-mcp": {
      "command": "gazebo-mcp",
      "args": ["serve"],
      "env": {
        "GAZEBO_MCP_MODE": "mock"
      }
    }
  }
}
```

If the host asks for a working directory, use the repository root or any
directory where the Python environment can resolve the installed `gazebo-mcp`
console script.

## Live bridge example

Start from mock mode first. When a bridge is available, switch only the mode and
bridge-specific environment variables required by your deployment:

```json
{
  "mcpServers": {
    "gazebo-mcp": {
      "command": "gazebo-mcp",
      "args": ["serve"],
      "env": {
        "GAZEBO_MCP_MODE": "live",
        "GAZEBO_MCP_BRIDGE_URL": "http://127.0.0.1:8765"
      }
    }
  }
}
```

Keep the URL local unless you explicitly trust the bridge. The MCP host should
not contain secrets in this configuration.

## Troubleshooting

Run these commands from the same shell or virtual environment used by the host:

```powershell
gazebo-mcp version
gazebo-mcp doctor
gazebo-mcp call world_info
gazebo-mcp call snapshot
```

If the host cannot find `gazebo-mcp`, use the absolute path to the virtual
environment's console script as the `command`, or reinstall with
`pip install -e ".[dev]"`.

If the server starts but no Gazebo instance is available, confirm that
`GAZEBO_MCP_MODE` is set to `mock`. Mock mode is intentionally offline-readable
and should be the default for demos, tests, and first-time setup.
