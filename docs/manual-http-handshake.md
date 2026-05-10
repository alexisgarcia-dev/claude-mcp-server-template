# Manual HTTP handshake — Streamable HTTP transport

The MCP Streamable HTTP transport (spec 2025-11-25) requires a multi-step lifecycle. The [fastmcp Python Client](https://gofastmcp.com) handles this transparently — this page is for raw `curl` / PowerShell debugging or for understanding the wire protocol.

## 3-step protocol

### Step 1 — `initialize`

```bash
curl -i -X POST http://127.0.0.1:8000/mcp \
  -H "Authorization: Bearer demo-readonly" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}'
```

Capture the `Mcp-Session-Id` response header — required for all subsequent requests.

### Step 2 — `notifications/initialized`

```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Authorization: Bearer demo-readonly" \
  -H "Mcp-Session-Id: <session-id-from-step-1>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}'
```

Server replies `202 Accepted` (notification, no response body).

### Step 3 — `tools/list` (or `tools/call`, `resources/read`, `prompts/get`…)

```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Authorization: Bearer demo-readonly" \
  -H "Mcp-Session-Id: <session-id-from-step-1>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

## Response format gotcha

The response body may be raw JSON OR a Server-Sent Events (SSE) stream depending on server configuration. SSE format:

```
event: message
data: {"jsonrpc":"2.0","id":2,"result":{"tools":[...]}}
```

Parse the JSON payload from the `data: ` line. See `healthcheck.py` in this repo for a reference Python implementation handling both formats.

## References

- [MCP spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — Streamable HTTP transport
- `healthcheck.py` — production-grade implementation with JSON + SSE parsers
- [gofastmcp.com](https://gofastmcp.com) — FastMCP 3.2.4 documentation
