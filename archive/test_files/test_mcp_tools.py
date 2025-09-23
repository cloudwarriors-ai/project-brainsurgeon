#!/usr/bin/env python3

import sys
import inspect
import importlib.util

# Import the MCP server module
spec = importlib.util.spec_from_file_location("mcp_server", "/root/code/project-brainsurgeon/mcp_server.py")
mcp_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_server)

# Get the FastMCP app instance
app = mcp_server.app

# List all registered tools
print("Registered MCP tools:")
print("FastMCP app attributes:", dir(app))

# Try to access tools
try:
    tools = app.get_tools()
    print("Available tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
        
    # Check specifically for submit_prompt
    submit_tools = [t for t in tools if 'submit' in t.name.lower()]
    if submit_tools:
        print(f"\n✅ Found submit-related tools: {[t.name for t in submit_tools]}")
    else:
        print("\n❌ No submit-related tools found")
        
except Exception as e:
    print(f"Error getting tools: {e}")
    
# Alternative: check _tool_manager
if hasattr(app, '_tool_manager'):
    print(f"\nTool manager tools: {app._tool_manager._tools.keys()}")
    if 'tui_submit_prompt' in app._tool_manager._tools:
        print("✅ tui_submit_prompt found in tool manager!")
    else:
        print("❌ tui_submit_prompt NOT found in tool manager!")

# Check the MCP server module for function definitions
print("\nFunctions in mcp_server module:")
for name, obj in inspect.getmembers(mcp_server):
    if inspect.isfunction(obj) and name.startswith('tui_'):
        print(f"- {name}: {obj.__doc__}")

# Specifically check for submit function
if hasattr(mcp_server, 'tui_submit_prompt'):
    print("\n✅ tui_submit_prompt function exists in module!")
else:
    print("\n❌ tui_submit_prompt function NOT found in module!")