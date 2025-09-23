#!/usr/bin/env python3
"""
Demo script showing multi-connection TUI management.
This demonstrates the new functionality with the actual MCP server.
"""

import asyncio
import json
import sys
import os
import subprocess

# Add the current directory to path so we can import from mcp_server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def demo_multi_connection():
    """Demonstrate the multi-connection functionality."""
    
    print("🚀 Multi-Connection TUI Demo")
    print("=" * 40)
    
    # Import the functions from our MCP server
    try:
        from mcp_server import (
            add_connection, list_connections, set_active_connection,
            get_connection_info, remove_connection, show_toast,
            tui_get_sessions, tui_test_connection
        )
        print("✅ Successfully imported MCP server functions")
    except ImportError as e:
        print(f"❌ Failed to import MCP server functions: {e}")
        return
    
    print("\n1. Testing Connection Management...")
    
    # Add a test connection (using the same localhost for demo)
    print("   Adding test connection...")
    result = await add_connection(
        connection_id="demo-project",
        url="http://localhost:7777",
        project_name="Demo Project",
        description="Test connection for demo"
    )
    print(f"   Add result: {result}")
    
    # List connections
    print("\n   Listing all connections...")
    connections = await list_connections()
    print(f"   Found {len(connections.get('connections', []))} connections:")
    for conn in connections.get('connections', []):
        print(f"     - {conn['connection_id']}: {conn['url']} ({conn.get('project_name', 'N/A')})")
    
    # Set active connection
    print("\n   Setting active connection...")
    result = await set_active_connection("demo-project")
    print(f"   Set active result: {result}")
    
    # Get connection info
    print("\n   Getting connection info...")
    info = await get_connection_info("demo-project")
    print(f"   Connection info: {json.dumps(info, indent=2)}")
    
    print("\n2. Testing TUI Functions with Connection ID...")
    
    # Test connection
    print("   Testing connection...")
    test_result = await tui_test_connection("http://localhost:7777")
    print(f"   Connection test: {test_result}")
    
    # Try to get sessions (if TUI is running)
    print("   Getting sessions...")
    try:
        sessions = await tui_get_sessions(connection_id="demo-project")
        print(f"   Sessions result: {sessions}")
    except Exception as e:
        print(f"   Sessions error (TUI may not be running): {e}")
    
    # Try to show toast (if TUI is running)
    print("   Sending toast notification...")
    try:
        toast_result = await show_toast(
            "Hello from multi-connection demo!",
            connection_id="demo-project"
        )
        print(f"   Toast result: {toast_result}")
    except Exception as e:
        print(f"   Toast error (TUI may not be running): {e}")
    
    print("\n3. Cleanup...")
    
    # Remove the test connection
    print("   Removing test connection...")
    result = await remove_connection("demo-project")
    print(f"   Remove result: {result}")
    
    # Verify it's gone
    connections = await list_connections()
    print(f"   Connections after removal: {len(connections.get('connections', []))}")
    
    print("\n✅ Demo completed!")
    print("\nNext steps:")
    print("1. Start your MCP server: python3 mcp_server.py")
    print("2. Connect to multiple OpenCode TUI instances")
    print("3. Use the new connection management tools")

if __name__ == "__main__":
    asyncio.run(demo_multi_connection())