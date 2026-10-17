#!/usr/bin/env python3
"""Probe MCP stdio initialization and tool enumeration, without touching a target."""
import json
import os
import selectors
import subprocess
import sys
import time


def rpc(method, message_id=None, params=None):
    payload = {"jsonrpc": "2.0", "method": method}
    if message_id is not None:
        payload["id"] = message_id
    if params is not None:
        payload["params"] = params
    return (json.dumps(payload, separators=(",", ":")) + "\n").encode()


def probe(command, timeout=90):
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, bufsize=0)
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    buffer = b""
    deadline = time.monotonic() + timeout

    def recv(message_id):
        nonlocal buffer
        while time.monotonic() < deadline:
            if b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if not line.strip():
                    continue
                result = json.loads(line)
                if result.get("id") == message_id:
                    if "error" in result:
                        raise RuntimeError(f"MCP error for id {message_id}: {result['error']}")
                    return result["result"]
                continue
            events = selector.select(timeout=max(0.0, min(0.5, deadline - time.monotonic())))
            if events:
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError("MCP stdout closed before response")
                buffer += chunk
                if len(buffer) > 32_000_000:
                    raise RuntimeError("MCP response exceeds 32 MB limit")
            elif process.poll() is not None:
                raise RuntimeError(f"MCP exited before response (code {process.returncode})")
        raise TimeoutError(f"No MCP response to id {message_id} within {timeout}s")

    try:
        process.stdin.write(rpc("initialize", 1, {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "pryntor-rea-smoke", "version": "0.1"}
        }))
        process.stdin.flush()
        hello = recv(1)
        if not isinstance(hello, dict) or not hello.get("protocolVersion"):
            raise RuntimeError("MCP initialize returned no negotiated protocol")
        process.stdin.write(rpc("notifications/initialized"))
        process.stdin.write(rpc("tools/list", 2, {}))
        process.stdin.flush()
        listing = recv(2)
        tools = listing.get("tools") if isinstance(listing, dict) else None
        if not isinstance(tools, list) or not tools:
            raise RuntimeError("MCP tools/list returned zero or invalid tools")
        names = [tool.get("name") for tool in tools]
        if not all(isinstance(name, str) and name for name in names):
            raise RuntimeError("MCP tool names invalid")
        print(json.dumps({"status": "mcp-handshake-and-tool-enumeration-only",
                          "protocol": hello["protocolVersion"], "tool_count": len(tools),
                          "has_js_analysis": "analyze_javascript_application" in names}))
        return 0
    finally:
        selector.close()
        process.kill() if process.poll() is None else None
        try:
            process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()


def self_test():
    assert json.loads(rpc("tools/list", 2, {}).decode())["id"] == 2
    fake = """import json,sys
for raw in sys.stdin:
 p=json.loads(raw)
 if p.get('method')=='initialize':
  print(json.dumps({'jsonrpc':'2.0','id':p['id'],'result':{'protocolVersion':'2025-03-26','capabilities':{},'serverInfo':{'name':'fake','version':'0'}}}),flush=True)
 elif p.get('method')=='tools/list':
  print(json.dumps({'jsonrpc':'2.0','id':p['id'],'result':{'tools':[{'name':'analyze_javascript_application','description':'X'*3_000_000,'inputSchema':{'type':'object'}}]}}),flush=True)
"""
    assert probe([sys.executable, "-u", "-c", fake], timeout=10) == 0
    print("PASS: local transport self-test (synthetic server, NOT REA)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    elif len(sys.argv) > 2 and sys.argv[1] == "--":
        sys.exit(probe(sys.argv[2:]))
    else:
        sys.exit("Usage: rea_mcp_probe.py --self-test | -- npx -y rea-agents@6.5.0 mcp")
