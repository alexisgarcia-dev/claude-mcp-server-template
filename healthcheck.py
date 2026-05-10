"""validates auth + transport + MCP session lifecycle (initialize handshake) + tool registration in one full-protocol round-trip"""

import json
import os
import sys

import httpx


def _parse_mcp_response(resp: httpx.Response) -> dict | None:
    """Parse MCP response: JSON direct OR Server-Sent Events stream (data: {...})."""
    text = resp.text
    # Try JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fallback: SSE stream — extract first data: payload
    for line in text.splitlines():
        if line.startswith("data: "):
            try:
                return json.loads(line[len("data: "):])
            except json.JSONDecodeError:
                continue
    return None


def main() -> int:
    base_url = os.getenv("MCP_HEALTHCHECK_URL", "http://localhost:8000/mcp")
    token = os.getenv("HEALTHCHECK_TOKEN", "demo-readonly")
    timeout_seconds = float(os.getenv("HEALTHCHECK_TIMEOUT", "5.0"))
    base_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            # Step 1: initialize
            init_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "healthcheck", "version": "1.0"},
                },
            }
            init_resp = client.post(base_url, json=init_payload, headers=base_headers)
            if init_resp.status_code != 200:
                print(f"healthcheck: initialize HTTP {init_resp.status_code}", file=sys.stderr)
                return 1
            session_id = init_resp.headers.get("Mcp-Session-Id")
            if not session_id:
                print("healthcheck: no Mcp-Session-Id in initialize response", file=sys.stderr)
                return 1

            session_headers = {**base_headers, "Mcp-Session-Id": session_id}

            # Step 2: notifications/initialized
            notif_payload = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
            client.post(base_url, json=notif_payload, headers=session_headers)

            # Step 3: tools/list with session
            tools_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }
            tools_resp = client.post(base_url, json=tools_payload, headers=session_headers)
            if tools_resp.status_code != 200:
                print(f"healthcheck: tools/list HTTP {tools_resp.status_code}", file=sys.stderr)
                return 1

            data = _parse_mcp_response(tools_resp)
            if data is None:
                print(
                    f"healthcheck: tools/list response unparseable (Content-Type: {tools_resp.headers.get('Content-Type', 'unknown')})",
                    file=sys.stderr,
                )
                return 1
            if "error" in data or "result" not in data:
                err_class = type(data.get("error", "")).__name__
                print(f"healthcheck: tools/list JSON-RPC {err_class}", file=sys.stderr)
                return 1
            tools = data["result"].get("tools", [])
            if len(tools) < 1:
                print("healthcheck: no tools registered", file=sys.stderr)
                return 1
            return 0
    except (httpx.RequestError, json.JSONDecodeError) as exc:
        # Token-leak guard: log only exception class + truncated message
        print(f"healthcheck: {type(exc).__name__}: {str(exc)[:200]}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
