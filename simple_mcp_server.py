#!/usr/bin/env python3
"""
Simplified MCP server for OpenCode bridge with dynamic connection capabilities.
This version focuses on the core functionality without heavy dependencies.
"""

import asyncio
import json
import time
import httpx
from typing import Optional, Dict, Any

class OpenCodeBridgeServer:
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
        self.event_queue = asyncio.Queue()
        self.running = False
    
    def get_client(self):
        """Get the active client if connected."""
        if self.connection_state["client"] and self.connection_state["connected"]:
            return self.connection_state["client"]
        return None
    
    async def establish_connection(self, host: str, port: int, timeout: int = 10):
        """Establish connection to OpenCode server at specific host and port."""
        try:
            base_url = f"http://{host}:{port}"
            test_client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
            
            print(f"🔍 Establishing connection to {base_url}...")
            
            # Test basic connectivity
            server_responsive = False
            endpoints_to_try = ["/app", "/doc", "/"]
            
            for endpoint in endpoints_to_try:
                try:
                    response = await test_client.get(endpoint, timeout=5)
                    if response.status_code in [200, 404]:
                        server_responsive = True
                        break
                except:
                    continue
            
            if not server_responsive:
                await test_client.aclose()
                return {
                    "success": False,
                    "error": "Server not responding",
                    "host": host,
                    "port": port
                }
            
            # Test event stream
            event_accessible = False
            try:
                async with test_client.stream("GET", "/event", timeout=3) as stream:
                    if stream.status_code == 200:
                        event_accessible = True
                        print(f"📡 Event stream established")
            except:
                pass
            
            # Close old connection if exists
            if self.connection_state["client"]:
                await self.connection_state["client"].aclose()
            
            # Update connection state
            self.connection_state.update({
                "client": test_client,
                "host": host,
                "port": port,
                "connected": True,
                "tui_established": event_accessible,
                "connection_time": time.time()
            })
            
            print(f"✅ Connection established to {base_url}")
            print(f"   Event Stream: {'✅' if event_accessible else '❌'}")
            
            return {
                "success": True,
                "host": host,
                "port": port,
                "base_url": base_url,
                "event_stream_accessible": event_accessible,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "host": host,
                "port": port
            }
    
    async def get_connection_status(self):
        """Get current connection status."""
        return {
            "connected": self.connection_state["connected"],
            "host": self.connection_state["host"],
            "port": self.connection_state["port"],
            "tui_established": self.connection_state["tui_established"],
            "connection_time": self.connection_state["connection_time"],
            "uptime": time.time() - self.connection_state["connection_time"] if self.connection_state["connection_time"] else None
        }
    
    async def get_next_event(self):
        """Get the next event from the stream."""
        try:
            event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
            return event
        except asyncio.TimeoutError:
            return {"error": "No event available"}
    
    async def show_toast(self, message: str, variant: str, title: str = None):
        """Show a toast notification in the TUI."""
        client = self.get_client()
        if not client:
            return {"error": "No active connection. Use establish_connection first."}
        
        data = {"message": message, "variant": variant}
        if title:
            data["title"] = title
        
        # Try multiple possible endpoints
        endpoints = ["/tui/show-toast", "/tui/showToast", "/tui/toast"]
        
        for endpoint in endpoints:
            try:
                resp = await client.post(endpoint, json=data, timeout=5)
                if resp.status_code == 200:
                    return {"success": True, "endpoint": endpoint, "response": resp.json()}
            except:
                continue
        
        return {"error": "TUI toast endpoints not accessible"}
    
    async def event_listener(self):
        """Listen for events from the connected OpenCode server."""
        while self.running:
            try:
                client = self.get_client()
                if not client:
                    await asyncio.sleep(5)
                    continue
                
                async with client.stream("GET", "/event") as response:
                    if response.status_code == 200:
                        self.connection_state["tui_established"] = True
                        print(f"📡 Event listener connected")
                        
                        async for line in response.aiter_lines():
                            if not self.running:
                                break
                                
                            if line.startswith("data: "):
                                try:
                                    event = json.loads(line[6:])
                                    self.connection_state["last_event_time"] = time.time()
                                    await self.event_queue.put(event)
                                    print(f"📨 Event: {event.get('type', 'unknown')}")
                                except json.JSONDecodeError:
                                    pass
                    else:
                        print(f"Event stream error: {response.status_code}")
                        await asyncio.sleep(5)
                        
            except Exception as e:
                print(f"Event listener error: {e}")
                self.connection_state["tui_established"] = False
                await asyncio.sleep(5)
    
    async def start_event_listener(self):
        """Start the event listener."""
        self.running = True
        asyncio.create_task(self.event_listener())
    
    async def stop(self):
        """Stop the server and close connections."""
        self.running = False
        if self.connection_state["client"]:
            await self.connection_state["client"].aclose()

# Test the server functionality
async def test_server():
    """Test the OpenCode bridge server."""
    print("🚀 Testing OpenCode Bridge Server")
    print("=" * 40)
    
    server = OpenCodeBridgeServer()
    
    # Test connection establishment
    print("\n1. Testing connection establishment...")
    result = await server.establish_connection("localhost", 6969)
    print(f"Result: {result}")
    
    if result["success"]:
        # Start event listener
        print("\n2. Starting event listener...")
        await server.start_event_listener()
        
        # Test connection status
        print("\n3. Testing connection status...")
        status = await server.get_connection_status()
        print(f"Status: {status}")
        
        # Test TUI interaction
        print("\n4. Testing TUI interaction...")
        toast_result = await server.show_toast(
            message="MCP Server Test", 
            variant="info", 
            title="Connection Verified"
        )
        print(f"Toast result: {toast_result}")
        
        # Test event getting
        print("\n5. Testing event retrieval...")
        for i in range(3):
            event = await server.get_next_event()
            print(f"Event {i+1}: {event}")
        
        await server.stop()
        print("\n✅ Server test completed")
    else:
        print("❌ Connection failed, skipping other tests")

if __name__ == "__main__":
    asyncio.run(test_server())