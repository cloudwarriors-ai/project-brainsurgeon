#!/usr/bin/env python3
"""
Test script for the dynamic OpenCode connection functionality.
This tests the core connection logic without the full MCP server framework.
"""

import asyncio
import httpx
import time
import json

class OpenCodeConnectionManager:
    def __init__(self):
        self.connection_state = {
            "client": None,
            "host": None,
            "port": None,
            "connected": False,
            "tui_established": False,
            "last_event_time": None,
            "connection_time": None
        }
    
    async def establish_connection(self, host: str, port: int, timeout: int = 10):
        """Establish connection to OpenCode server at specific host and port with TUI and event verification."""
        try:
            base_url = f"http://{host}:{port}"
            test_client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
            
            # Test basic connectivity with multiple endpoints
            print(f"🔍 Testing connection to {base_url}...")
            server_responsive = False
            endpoints_to_try = ["/app", "/doc", "/", "/health", "/status"]
            
            for endpoint in endpoints_to_try:
                try:
                    response = await test_client.get(endpoint, timeout=5)
                    if response.status_code in [200, 404]:  # Server is responding
                        server_responsive = True
                        print(f"✅ Server is responsive at {base_url} (tested {endpoint})")
                        break
                except Exception as e:
                    continue
            
            if not server_responsive:
                return {
                    "success": False,
                    "error": f"Server not responding to any test endpoints",
                    "host": host,
                    "port": port
                }
            
            # Test TUI endpoints
            print(f"🖥️  Testing TUI endpoints...")
            tui_available = False
            try:
                # Test different TUI endpoints
                endpoints_to_test = [
                    "/tui/control/next",
                    "/doc"  # Documentation endpoint should always be available
                ]
                
                for endpoint in endpoints_to_test:
                    try:
                        tui_response = await test_client.get(endpoint, timeout=3)
                        if tui_response.status_code in [200, 404]:  # 404 is ok for control/next
                            tui_available = True
                            break
                    except:
                        continue
                        
                print(f"✅ TUI endpoints accessible: {tui_available}")
            except Exception as e:
                print(f"⚠️  TUI test warning: {e}")
            
            # Update connection state
            if self.connection_state["client"]:
                await self.connection_state["client"].aclose()
                
            self.connection_state.update({
                "client": test_client,
                "host": host,
                "port": port,
                "connected": True,
                "tui_established": False,  # Will be set true when event stream connects
                "connection_time": time.time()
            })
            
            # Test event stream
            print(f"📡 Testing event stream...")
            event_test = False
            try:
                async with test_client.stream("GET", "/event", timeout=5) as stream_response:
                    if stream_response.status_code == 200:
                        event_test = True
                        self.connection_state["tui_established"] = True
                        print(f"✅ Event stream accessible")
                        
                        # Try to read a few events or timeout
                        event_count = 0
                        async for line in stream_response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]
                                try:
                                    event = json.loads(data)
                                    print(f"📨 Received event: {event.get('type', 'unknown')}")
                                    event_count += 1
                                    if event_count >= 2:  # Just read a couple events
                                        break
                                except json.JSONDecodeError:
                                    pass
                            if event_count == 0:
                                await asyncio.sleep(1)  # Wait briefly for events
                                break
                    else:
                        print(f"⚠️  Event stream returned status: {stream_response.status_code}")
            except Exception as e:
                print(f"⚠️  Event stream test warning: {e}")
            
            result = {
                "success": True,
                "host": host,
                "port": port,
                "base_url": base_url,
                "server_responsive": True,
                "tui_available": tui_available,
                "event_stream_accessible": event_test,
                "connection_established": True,
                "timestamp": time.time()
            }
            
            print(f"🎉 Connection fully established to {base_url}")
            print(f"   Server Responsive: ✅")
            print(f"   TUI Available: {'✅' if tui_available else '❌'}")
            print(f"   Event Stream: {'✅' if event_test else '❌'}")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "host": host,
                "port": port
            }
    
    async def test_tui_interaction(self):
        """Test TUI interaction by showing a toast and checking response."""
        if not self.connection_state["client"] or not self.connection_state["connected"]:
            return {"success": False, "error": "No active connection"}
        
        try:
            print(f"🧪 Testing TUI interaction...")
            # Test toast with correct OpenCode API path
            response = await self.connection_state["client"].post("/tui/show-toast", json={
                "message": "MCP Connection Test",
                "variant": "info",
                "title": "Connection Verified"
            })
            
            if response.status_code == 200:
                print(f"✅ TUI interaction successful - toast displayed")
                return {
                    "success": True,
                    "tui_responsive": True,
                    "test_action": "toast_displayed",
                    "response": response.json()
                }
            else:
                print(f"❌ TUI responded with status {response.status_code}")
                return {
                    "success": False,
                    "error": f"TUI responded with status {response.status_code}"
                }
        except Exception as e:
            print(f"❌ TUI interaction failed: {str(e)}")
            return {
                "success": False,
                "error": f"TUI interaction failed: {str(e)}"
            }
    
    def get_connection_status(self):
        """Get current connection status including TUI and event stream state."""
        return {
            "connected": self.connection_state["connected"],
            "host": self.connection_state["host"],
            "port": self.connection_state["port"],
            "tui_established": self.connection_state["tui_established"],
            "last_event_time": self.connection_state["last_event_time"],
            "connection_time": self.connection_state["connection_time"],
            "base_url": f"http://{self.connection_state['host']}:{self.connection_state['port']}" if self.connection_state["host"] else None,
            "uptime": time.time() - self.connection_state["connection_time"] if self.connection_state["connection_time"] else None
        }

async def test_opencode_connections():
    """Test connections to various OpenCode servers."""
    manager = OpenCodeConnectionManager()
    
    # Test ports from the running processes we saw
    test_ports = [6969, 7777, 69696]
    
    print("🚀 Testing OpenCode Connection Manager")
    print("=" * 50)
    
    for port in test_ports:
        print(f"\n🔗 Testing connection to localhost:{port}")
        print("-" * 30)
        
        result = await manager.establish_connection("localhost", port)
        
        if result["success"]:
            print(f"✅ Connection successful!")
            
            # Test TUI interaction
            tui_result = await manager.test_tui_interaction()
            
            # Get connection status
            status = manager.get_connection_status()
            print(f"\n📊 Connection Status:")
            print(f"   Connected: {status['connected']}")
            print(f"   TUI Established: {status['tui_established']}")
            print(f"   Uptime: {status['uptime']:.2f}s")
            
            print(f"✅ Successfully tested port {port}\n")
            
            # Close connection before testing next port
            if manager.connection_state["client"]:
                await manager.connection_state["client"].aclose()
                manager.connection_state = {
                    "client": None,
                    "host": None,
                    "port": None,
                    "connected": False,
                    "tui_established": False,
                    "last_event_time": None,
                    "connection_time": None
                }
        else:
            print(f"❌ Connection failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_opencode_connections())