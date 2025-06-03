#!/usr/bin/env python3
"""
Simple MCP client to test the Google Calendar server
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime, timedelta

async def test_with_mcp_client():
    """Test the server using a simple MCP client."""
    
    print("🧪 Testing Google Calendar MCP Server with client...\n")
    
    # Test messages to send to the server
    test_messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "list_events",
                "arguments": {
                    "calendar_id": "primary",
                    "max_results": 5
                }
            }
        }
    ]
    
    try:
        # Start the server process
        print("🚀 Starting MCP server...")
        process = subprocess.Popen(
            [sys.executable, "-c", """
import asyncio
import sys
sys.path.insert(0, '.')
from src.google_calendar_mcp.server import main
asyncio.run(main())
"""],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialize message first
        init_message = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialize message...")
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        if response:
            print(f"📥 Initialize response: {response.strip()}")
        
        # Send test messages
        for i, message in enumerate(test_messages, 1):
            print(f"\n📤 Sending test message {i}: {message['method']}")
            process.stdin.write(json.dumps(message) + "\n")
            process.stdin.flush()
            
            # Read response with timeout
            try:
                response = process.stdout.readline()
                if response:
                    response_data = json.loads(response.strip())
                    print(f"📥 Response: {json.dumps(response_data, indent=2)}")
                else:
                    print("❌ No response received")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response}")
            
            # Check for errors
            if process.poll() is not None:
                stderr_output = process.stderr.read()
                print(f"❌ Server process ended unexpectedly: {stderr_output}")
                break
        
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'process' in locals():
            process.terminate()

def simple_server_test():
    """Simple test to verify server starts and can list tools."""
    print("🔧 Simple server startup test...\n")
    
    try:
        # Try to import and initialize
        from src.google_calendar_mcp.server import GoogleCalendarServer
        server = GoogleCalendarServer()
        print("✅ Server imports and initializes successfully")
        
        # Try to get tools (this should work without authentication)
        import asyncio
        
        async def get_tools():
            for handler_name, handler in server.app._request_handlers.items():
                if "list_tools" in str(handler_name):
                    tools = await handler()
                    return tools
            return []
        
        tools = asyncio.run(get_tools())
        print(f"✅ Server provides {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Google Calendar MCP Server Test Suite")
    print("=" * 50)
    
    # Run simple test first
    if simple_server_test():
        print("\n" + "=" * 50)
        print("Running MCP client test...")
        print("=" * 50)
        asyncio.run(test_with_mcp_client())
    else:
        print("\n❌ Basic server test failed. Fix issues before proceeding.")