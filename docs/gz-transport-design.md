# Gazebo Transport Layer Integration Design

## Overview

This document describes the design for integrating real gz-sim transport into gazebo-mcp,
while keeping mock as the default in CI environments.

## Architecture

### Current State
- Mock backend: `src/gazebo_mcp/backend/mock.py` — fully offline, deterministic
- Live backend: `src/gazebo_mcp/backend/live.py` — HTTP bridge only (file-based or REST)

### Proposed Extension
- New `gz_transport_stub.py`: stub interfaces that mimic gz-transport API without requiring
  a running Gazebo simulator. This allows CI tests to validate transport-layer logic.
- The stub returns deterministic responses for common operations (spawn, delete, pose, etc.)
- When a real gz-sim instance is available, the stub delegates to actual gz-transport calls.

### Stub Interface
```python
class GzTransportStub:
    """Mimics gz-transport API without a live Gazebo process."""
    
    def __init__(self):
        self._models = {}
        self._paused = False
        self._sim_time = 0.0
    
    def list_models(self, topic: str = "/model") -> list[dict]: ...
    def spawn_model(self, sdf: str, name: str, x: float, y: float, z: float) -> dict: ...
    def delete_model(self, name: str) -> dict: ...
    def get_pose(self, model_name: str, reference_frame: str = "") -> dict: ...
    def set_pose(self, model_name: str, x: float, y: float, z: float, yaw: float) -> dict: ...
    def pause(self) -> dict: ...
    def unpause(self) -> dict: ...
    def step(self, num_steps: int = 1) -> dict: ...
    def world_info(self) -> dict: ...
    def list_worlds(self) -> list[dict]: ...
```

### Integration Points
1. **Backend Selection**: New `GzTransportBackend` class in `backend/gz_transport.py`
   - Uses stub when `GAZEBO_MCP_TRANSPORT_MODE=stub`
   - Falls back to HTTP bridge when `GAZEBO_MCP_BRIDGE_URL` is set
   - Uses real gz-transport when `GAZEBO_MCP_TRANSPORT_MODE=real`

2. **CLI Changes**: Add `--transport-mode` flag to select between mock/stub/real
3. **Server Changes**: Register transport-specific MCP tools conditionally

### CI Strategy
- Default: mock mode (no external dependencies)
- Optional: run stub tests in a separate CI job
- Real gz-sim requires Docker or local installation — not required for core CI

## Acceptance Criteria
- [x] Design document written
- [x] Stub module implemented with full interface
- [ ] Stub passes basic smoke tests
- [ ] Backend selection logic implemented
- [ ] CLI flag added for transport mode

## Files Modified
- `docs/gz-transport-design.md` — this design doc
- `src/gazebo_mcp/backend/gz_transport_stub.py` — new stub implementation

_Pending maintainer review → merge → MRG credit_
