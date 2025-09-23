#!/usr/bin/env python3
"""Simple test of single OpenCode connection"""

import asyncio
import httpx
import json

async def test_single_connection():
    """Test a single OpenCode connection with TUI interaction."""
    
    host = "localhost"
    port = 6969
    base_url = f"http://{host}:{port}"
    
    print(f"🔗 Testing OpenCode connection to {base_url}")
    
    async with httpx.AsyncClient(base_url=base_url, timeout=10) as client:
        # Test server response
        print("1. Testing server connectivity...")
        try:
            response = await client.get("/app")
            print(f"   ✅ Server responded: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Server test failed: {e}")
            return
        
        # Test event stream
        print("2. Testing event stream...")
        try:
            async with client.stream("GET", "/event", timeout=3) as stream:
                print(f"   ✅ Event stream connected: {stream.status_code}")
                
                # Read one event
                async for line in stream.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            print(f"   📨 Event received: {event.get('type', 'unknown')}")
                            break
                        except:
                            pass
                    break
        except Exception as e:
            print(f"   ⚠️  Event stream warning: {e}")
        
        # Test TUI interaction
        print("3. Testing TUI interaction...")
        tui_endpoints = [
            "/tui/show-toast",
            "/tui/showToast", 
            "/tui/toast"
        ]
        
        toast_data = {
            "message": "Connection Test Success!",
            "variant": "success",
            "title": "MCP Test"
        }
        
        for endpoint in tui_endpoints:
            try:
                response = await client.post(endpoint, json=toast_data, timeout=5)
                print(f"   Endpoint {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ TUI interaction successful!")
                    break
            except Exception as e:
                print(f"   Endpoint {endpoint}: Error - {e}")
        
        print(f"\n🎉 Connection test completed for {base_url}")

if __name__ == "__main__":
    asyncio.run(test_single_connection())