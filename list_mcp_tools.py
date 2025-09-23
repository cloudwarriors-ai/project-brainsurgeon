#!/usr/bin/env python3
"""
Simple script to list available MCP tools by using the get_available_tools endpoint.
This helps verify that the tools are registered and available.
"""

import subprocess
import json
import os

# Run curl to invoke the opencode-bridge_get_available_tools function
def get_tools():
    try:
        # Try to get tools from MCP server
        cmd = ["curl", "-s", "-X", "POST", 
               "http://localhost:7777/opencode-bridge/tools", 
               "-H", "Content-Type: application/json", 
               "-d", "{}"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                return data
            except json.JSONDecodeError:
                print(f"Error parsing response: {result.stdout}")
                return None
        else:
            print(f"Command failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # Check if MCP_TOOLS.md exists
    if os.path.exists("MCP_TOOLS.md"):
        print(f"✅ MCP_TOOLS.md documentation file exists")
    else:
        print(f"❌ MCP_TOOLS.md documentation file does not exist")
    
    # Check if opencode.json has been updated
    try:
        with open("opencode.json", "r") as f:
            config = json.load(f)
            if "description" in config.get("mcp", {}).get("opencode-bridge", {}):
                print(f"✅ opencode.json has updated bridge description")
            else:
                print(f"❌ opencode.json is missing bridge description")
    except Exception as e:
        print(f"❌ Error checking opencode.json: {e}")
    
    # Try to get tools from the MCP server
    tools = get_tools()
    if tools and "tools" in tools:
        print(f"\n✅ Successfully retrieved {len(tools['tools'])} tools from MCP server")
        print("\nAvailable opencode-bridge tools:")
        print("=" * 40)
        for tool in tools["tools"]:
            print(f"• {tool['name']}")
            print(f"  {tool['description']}")
            print()
    else:
        print("\n❌ Failed to retrieve tools from MCP server")
        print("This could be due to the MCP server not running or the endpoint not being available.")
        print("Check if the server is running with: ps aux | grep mcp_server.py")

if __name__ == "__main__":
    main()