# Live bridge HTTP contract

`gazebo-mcp` can run in `live` mode by forwarding read-only status calls to a
local Gazebo bridge. The first live HTTP contract is intentionally small:
`/health` for connectivity and `/world_info` for world status.

Mock mode remains the default. Use live mode only when a trusted local bridge is
available:

```powershell
$env:GAZEBO_MCP_MODE = "live"
$env:GAZEBO_MCP_BRIDGE_URL = "http://127.0.0.1:8765"
gazebo-mcp doctor
gazebo-mcp call world_info
```

Do not put secrets in this configuration. The bridge URL should normally point
to loopback or another trusted local endpoint.

## GET /health

Returns bridge connectivity and runtime metadata used by `LiveBackend.doctor()`.

OpenAPI-style notes:

```yaml
get:
  summary: Read live Gazebo bridge health
  responses:
    "200":
      description: Bridge is reachable and ready for read-only status calls.
      content:
        application/json:
          schema:
            type: object
            required: [ok]
            properties:
              ok:
                type: boolean
              service:
                type: string
              mode:
                type: string
              version:
                type: string
              gazebo:
                type: object
```

Example:

```json
{
  "ok": true,
  "service": "gazebo-bridge",
  "mode": "live",
  "version": "0.1.0",
  "gazebo": {
    "transport": "gz-sim",
    "world": "default"
  }
}
```

`gazebo-mcp doctor` wraps this response:

```json
{
  "ok": true,
  "connected": true,
  "mode": "live",
  "bridge": "http",
  "health": {
    "ok": true,
    "service": "gazebo-bridge",
    "mode": "live"
  }
}
```

## GET /world_info

Returns the active world status used by `LiveBackend.world_info()`.

OpenAPI-style notes:

```yaml
get:
  summary: Read active Gazebo world status
  responses:
    "200":
      description: Current world status.
      content:
        application/json:
          schema:
            type: object
            required: [world, paused, sim_time_sec]
            properties:
              world:
                type: string
              paused:
                type: boolean
              sim_time_sec:
                type: number
              model_count:
                type: integer
              physics:
                oneOf:
                  - type: string
                  - type: object
```

Example:

```json
{
  "world": "default",
  "paused": false,
  "sim_time_sec": 12.5,
  "model_count": 2,
  "physics": "ode"
}
```

`gazebo-mcp call world_info` adds `ok: true` when the bridge returns a valid JSON
object:

```json
{
  "ok": true,
  "world": "default",
  "paused": false,
  "sim_time_sec": 12.5,
  "model_count": 2,
  "physics": "ode"
}
```

## Failure behavior

Live mode fails closed. If the bridge is missing, down, returns invalid JSON, or
returns non-object JSON, `gazebo-mcp` reports `ok: false` and does not fall back
to mock data.

Example when the bridge is down:

```json
{
  "ok": false,
  "connected": false,
  "mode": "live",
  "error": "<connection error>"
}
```

This makes host integrations safe to diagnose: mock tests stay offline and live
status calls cannot silently report simulated data when a real bridge is
expected.
