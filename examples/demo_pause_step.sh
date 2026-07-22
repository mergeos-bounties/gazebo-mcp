#!/usr/bin/env bash
# Demo: Pause/Step simulation tools (bounty #22)
# Requires: python3, gazebo-mcp installed
# Usage: bash examples/demo_pause_step.sh

set -euo pipefail

echo "=== Gazebo MCP: Pause/Step Demo ==="
echo ""

# Start mock server in background
gazebo-mcp server &
SERVER_PID=$!
sleep 2

# Test via MCP tool calls (using stdin/stdout protocol)
echo "1. World info (initial state):"
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"gazebo_world_info","arguments":{}}}' | gazebo-mcp 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "  (stdin mode not available, using Python)"

# Python-based demo
python3 << 'PYEOF'
from gazebo_mcp.backend import get_backend
from gazebo_mcp.config import set_mode

set_mode("mock")
b = get_backend()

print(f"World: {b.world_info()['world']}")
print(f"Paused: {b.world_info()['paused']}")
print()

# Pause simulation
print("2. Pausing simulation...")
result = b.pause()
print(f"   Result: {result}")
print()

# Verify paused state
info = b.world_info()
print(f"   World paused: {info['paused']}")
print()

# Step simulation
print("3. Stepping simulation 5 times...")
result = b.step(5)
print(f"   Result: steps={result['steps']}, sim_time={result.get('sim_time', 'N/A')}")
print()

# Step again
print("4. Stepping 3 more times...")
result = b.step(3)
print(f"   Result: steps={result['steps']}, sim_time={result.get('sim_time', 'N/A')}")
print()

# Unpause
print("5. Unpausing simulation...")
result = b.unpause()
print(f"   Result: {result}")
print()

# Verify unpaused
info = b.world_info()
print(f"   World paused: {info['paused']}")
print()

# Step while unpaused
print("6. Stepping while unpaused (should auto-pause)...")
result = b.step(2)
print(f"   Result: steps={result['steps']}, sim_time={result.get('sim_time', 'N/A')}")
print()

print("=== Demo complete ===")
PYEOF
