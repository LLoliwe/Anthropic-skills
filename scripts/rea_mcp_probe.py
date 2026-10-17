#!/usr/bin/env python3
"""Probe MCP stdio initialization and tool enumeration, without touching a target."""
import json
import os
from pathlib import Path
import signal
import tempfile
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


def extract_fixture_evidence(result):
    if not isinstance(result, dict) or result.get("isError"):
        raise RuntimeError("REA MCP tool reported an error")
    candidates = [result.get("structuredContent")]
    for part in result.get("content", []):
        if isinstance(part, dict) and part.get("type") == "text":
            try:
                candidates.append(json.loads(part.get("text", "")))
            except (TypeError, ValueError):
                pass
    for entry in candidates:
        if not isinstance(entry, dict):
            continue
        for item in (entry, entry.get("result"), entry.get("evidence")):
            if isinstance(item, dict) and item.get("operation") == "analyze_javascript_application":
                return item
    raise RuntimeError("REA tool returned no parseable JavaScript analysis Evidence")


def validate_fixture_evidence(evidence):
    if evidence.get("provider", {}).get("id") != "rea-javascript-application":
        raise RuntimeError("Unexpected REA static-analysis provider")
    result = evidence.get("normalized_result")
    graph = result.get("graph") if isinstance(result, dict) else None
    if not isinstance(graph, dict) or len(graph.get("nodes", [])) < 2:
        raise RuntimeError("Missing static-analysis graph")
    observed = [str(obs.get("label", "")) for node in graph["nodes"]
                for obs in node.get("observations", []) if isinstance(obs, dict)]
    if not all(any(filename in name for name in observed) for filename in ("index.js", "format.js")):
        raise RuntimeError("Evidence did not observe both fixture modules")
    if not any(edge.get("relation") == "imports" for edge in graph.get("edges", [])):
        raise RuntimeError("Evidence did not recover fixture import relationship")
    return len(graph["nodes"])


def probe(command, timeout=90, fixture=None):
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, bufsize=0,
                               start_new_session=(os.name == 'posix'))
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    buffer = b""
    deadline = time.monotonic() + timeout

    def recv(message_id):
        nonlocal buffer
        while time.monotonic() < deadline:
            if len(buffer) > 32_000_000:
                raise RuntimeError("MCP stdout frame exceeds 32 MB limit")
            if b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if not line.strip():
                    continue
                if len(line) > 32_000_000:
                    raise RuntimeError("MCP JSON frame exceeds 32 MB limit")
                try:
                    result = json.loads(line)
                except ValueError as exc:
                    raise RuntimeError("MCP stdout was not valid JSON") from exc
                if not isinstance(result, dict):
                    raise RuntimeError("MCP response was not a JSON object")
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
                          "has_js_analysis": "analyze_javascript_application" in names}), flush=True)
        if fixture is not None:
            if "analyze_javascript_application" not in names:
                raise RuntimeError("Required JavaScript analysis tool not advertised")
            target = Path(fixture).resolve(strict=True)
            if target.name != "rea-owned-js" or not target.is_dir():
                raise RuntimeError("Only an original rea-owned-js directory is allowed")
            process.stdin.write(rpc("tools/call", 3, {
                "name": "analyze_javascript_application",
                "arguments": {"input_path": str(target), "format": "directory"}}))
            process.stdin.flush()
            evidence = extract_fixture_evidence(recv(3))
            nodes = validate_fixture_evidence(evidence)
            print(json.dumps({"status": "real-rea-mcp-js-call-passed",
                              "operation": evidence["operation"],
                              "graph_nodes": nodes,
                              "evidence_id": evidence.get("evidence_id")}), flush=True)
        return 0
    finally:
        selector.close()
        if process.poll() is None:
            try:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
            except ProcessLookupError:
                pass
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
 elif p.get('method')=='tools/call':
  print(json.dumps({'jsonrpc':'2.0','id':p['id'],'result':{'isError':False,'structuredContent':{'operation':'analyze_javascript_application','provider':{'id':'rea-javascript-application'},'normalized_result':{'graph':{'nodes':[{'observations':[{'label':'index.js'}]},{'observations':[{'label':'format.js'}]}],'edges':[{'relation':'imports'}]}}}}}),flush=True)
"""
    with tempfile.TemporaryDirectory() as base:
        target = Path(base) / "rea-owned-js"
        target.mkdir()
        assert probe([sys.executable, "-u", "-c", fake], timeout=10, fixture=str(target)) == 0
    noisy = """import json,sys
for raw in sys.stdin:
 p=json.loads(raw)
 if p.get('method')=='initialize':
  sys.stderr.write('X'*3_000_000);sys.stderr.flush()
  print(json.dumps({'jsonrpc':'2.0','id':p['id'],'result':{'protocolVersion':'2025-03-26'}}),flush=True)
 elif p.get('method')=='tools/list':
  print(json.dumps({'jsonrpc':'2.0','id':p['id'],'result':{'tools':[{'name':'probe'}]}}),flush=True)
"""
    assert probe([sys.executable, "-u", "-c", noisy], timeout=10) == 0
    no_tools = """import json,sys
for raw in sys.stdin:
 p=json.loads(raw)
 if p.get('method')=='initialize':
  print(json.dumps({'jsonrpc':'2.0','id':p['id'],'result':{'protocolVersion':'2025-03-26'}}),flush=True)
 elif p.get('method')=='tools/list':
  print(json.dumps({'jsonrpc':'2.0','id':p['id'],'result':{'tools':[]}}),flush=True)
"""
    try:
        probe([sys.executable, "-u", "-c", no_tools], timeout=10)
        raise AssertionError("MCP empty tools must fail closed")
    except RuntimeError as exc:
        if "zero or invalid" not in str(exc):
            raise
    print("PASS: synthetic large catalog, tools/call, stderr flood and negative cases (NOT REA)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    elif len(sys.argv) > 4 and sys.argv[1] == "--call-js-target" and sys.argv[3] == "--":
        sys.exit(probe(sys.argv[4:], fixture=sys.argv[2]))
    elif len(sys.argv) > 2 and sys.argv[1] == "--":
        sys.exit(probe(sys.argv[2:]))
    else:
        sys.exit("Usage: rea_mcp_probe.py --self-test | -- npx ... mcp | --call-js-target DIR -- npx ... mcp")
