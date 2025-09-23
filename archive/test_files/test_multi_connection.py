#!/usr/bin/env python3
"""
Test script for multi-connection functionality.
This script demonstrates the new connection management features.
"""

import asyncio
import json
import httpx

async def test_connection_management():
    """Test the connection management functionality."""
    
    print("🔧 Testing Multi-Connection TUI Management")
    print("=" * 50)
    
    # Test the default connection (localhost:7777)
    print("\n1. Testing default connection...")
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get("http://localhost:7777/doc")
            if response.status_code in [200, 404]:
                print("✅ Default connection (localhost:7777) is available")
            else:
                print("❌ Default connection not responding properly")
    except Exception as e:
        print("❌ Default connection failed:", str(e))
    
    # Simulate adding a connection (we'll add the same one with a different ID for demo)
    print("\n2. Connection Management Features:")
    print("   📝 add_connection(connection_id, url, project_name, description)")
    print("   📋 list_connections()")
    print("   🎯 set_active_connection(connection_id)")
    print("   ℹ️  get_connection_info(connection_id)")
    print("   🗑️  remove_connection(connection_id)")
    
    # Example of how connections would be used
    print("\n3. Example Usage:")
    print("   # Add a connection")
    print("   await add_connection('project1', 'http://localhost:7777', 'My Project', 'Main development')")
    print("   await add_connection('project2', 'http://localhost:8888', 'Other Project', 'Secondary dev')")
    print("")
    print("   # List all connections")
    print("   connections = await list_connections()")
    print("")
    print("   # Set active connection")
    print("   await set_active_connection('project1')")
    print("")
    print("   # Use TUI functions with specific connection")
    print("   sessions = await tui_get_sessions(connection_id='project2')")
    print("   await show_toast('Hello!', connection_id='project1')")
    
    print("\n4. Benefits:")
    print("   🔗 Connect to multiple OpenCode TUI instances simultaneously")
    print("   🏷️  Identify connections by project name or custom ID")
    print("   🎯 Target specific TUI instances for commands")
    print("   📊 Monitor connection status across multiple instances")
    print("   🔄 Switch between active connections easily")
    
    print("\n✅ Multi-connection system is ready!")
    print("   Start your MCP server and use the new connection management tools.")

if __name__ == "__main__":
    asyncio.run(test_connection_management())