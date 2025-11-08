#!/usr/bin/env python3
"""
Test Syntropy MCP Server
- Starts server
- Waits for initialization
- Tests tool registration
- Calls tools
- Reports results
"""

import json
import subprocess
import sys
import time
from threading import Thread
from queue import Queue, Empty

class MCPClient:
    def __init__(self, build_path="build/index.js"):
        self.build_path = build_path
        self.process = None
        self.request_id = 0
        self.stderr_queue = Queue()
        self.response_queue = Queue()

    def start_server(self):
        """Start the MCP server process"""
        print("🚀 Starting syntropy MCP server...")
        self.process = subprocess.Popen(
            ["node", self.build_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Start threads to read stdout/stderr
        Thread(target=self._read_stderr, daemon=True).start()
        Thread(target=self._read_stdout, daemon=True).start()

        print("✅ Server process started")

    def _read_stderr(self):
        """Read stderr for logs"""
        for line in iter(self.process.stderr.readline, ''):
            if line:
                self.stderr_queue.put(line.strip())

    def _read_stdout(self):
        """Read stdout for JSON-RPC responses"""
        for line in iter(self.process.stdout.readline, ''):
            if line.strip():
                try:
                    data = json.loads(line)
                    self.response_queue.put(data)
                except json.JSONDecodeError:
                    pass  # Ignore non-JSON lines

    def send_request(self, method, params=None):
        """Send JSON-RPC request"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        json_str = json.dumps(request)
        self.process.stdin.write(json_str + "\n")
        self.process.stdin.flush()
        return self.request_id

    def send_notification(self, method, params=None):
        """Send JSON-RPC notification (no response expected)"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        json_str = json.dumps(notification)
        self.process.stdin.write(json_str + "\n")
        self.process.stdin.flush()

    def wait_for_response(self, request_id, timeout=30):
        """Wait for response to specific request"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.response_queue.get(timeout=0.5)
                if response.get("id") == request_id:
                    return response
                else:
                    # Put it back if it's for a different request
                    self.response_queue.put(response)
            except Empty:
                continue
        raise TimeoutError(f"No response for request {request_id} within {timeout}s")

    def wait_for_log(self, pattern, timeout=30):
        """Wait for specific log message"""
        start_time = time.time()
        logs = []
        while time.time() - start_time < timeout:
            try:
                log = self.stderr_queue.get(timeout=0.5)
                logs.append(log)
                if pattern in log:
                    return True, log
            except Empty:
                continue
        return False, "\n".join(logs[-10:])  # Return last 10 logs

    def stop_server(self):
        """Stop the server"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            print("🛑 Server stopped")


def test_syntropy_server():
    """Run full test suite"""
    client = MCPClient()

    try:
        # Step 1: Start server
        client.start_server()

        # Step 2: Wait for eager servers to initialize
        print("\n⏳ Waiting for eager servers to initialize...")
        success, log = client.wait_for_log("All eager servers ready", timeout=15)
        if not success:
            print(f"❌ FAIL: Servers didn't initialize\nLast logs:\n{log}")
            return False
        print("✅ Eager servers initialized")

        # Step 3: MCP Handshake - Initialize
        print("\n🤝 Sending initialize request...")
        req_id = client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        })

        response = client.wait_for_response(req_id, timeout=5)
        if "error" in response:
            print(f"❌ FAIL: Initialize failed: {response['error']}")
            return False
        print("✅ Initialize successful")

        # Step 4: Send initialized notification
        print("📢 Sending initialized notification...")
        client.send_notification("notifications/initialized")
        time.sleep(0.5)

        # Step 5: Request tools list
        print("\n📋 Requesting tools list...")
        req_id = client.send_request("tools/list")

        response = client.wait_for_response(req_id, timeout=5)
        if "error" in response:
            print(f"❌ FAIL: tools/list failed: {response['error']}")
            return False

        # DEBUG: Print full response
        print(f"📦 DEBUG: Full response: {json.dumps(response, indent=2)}")

        tools = response.get("result", {}).get("tools", [])
        if not tools:
            print("❌ FAIL: No tools returned")
            print(f"📦 DEBUG: Result object: {response.get('result', {})}")
            return False

        print(f"✅ Received {len(tools)} tools")

        # Step 6: Check tool name prefixes
        print("\n🔍 Checking tool name prefixes...")
        correct_prefix = 0
        wrong_prefix = 0

        for tool in tools[:5]:  # Check first 5
            name = tool.get("name", "")
            if name.startswith("mcp__syntropy__"):
                correct_prefix += 1
                print(f"  ✅ {name}")
            else:
                wrong_prefix += 1
                print(f"  ❌ {name} (missing prefix!)")

        if wrong_prefix > 0:
            print(f"\n❌ FAIL: {wrong_prefix} tools missing mcp__syntropy__ prefix")
            print(f"Expected format: mcp__syntropy__<server>_<tool>")
            print(f"Sample tools:")
            for tool in tools[:3]:
                print(f"  - {tool.get('name')}")
            return False

        print(f"✅ All checked tools have correct prefix")

        # Step 7: Try calling a tool (healthcheck)
        print("\n🏥 Testing tool call (healthcheck)...")
        req_id = client.send_request("tools/call", {
            "name": "mcp__syntropy__healthcheck",
            "arguments": {"detailed": False}
        })

        response = client.wait_for_response(req_id, timeout=10)
        if "error" in response:
            print(f"❌ FAIL: healthcheck call failed: {response['error']}")
            return False

        result = response.get("result", {})
        print(f"✅ Healthcheck successful")

        # Print health status
        content = result.get("content", [])
        if content:
            text = content[0].get("text", "")
            print(f"\n{text[:200]}...")  # First 200 chars

        return True

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        client.stop_server()


if __name__ == "__main__":
    print("=" * 60)
    print("Syntropy MCP Server Test")
    print("=" * 60)

    success = test_syntropy_server()

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ TESTS FAILED")
        print("=" * 60)
        sys.exit(1)
