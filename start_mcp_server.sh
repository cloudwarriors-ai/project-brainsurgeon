#!/bin/bash

# Kill any existing MCP server processes
pkill -f "mcp_server.py" || true

# Change to the project directory
cd /root/code/project-brainsurgeon

# Create a dedicated PID file for the MCP server
PID_FILE="/tmp/mcp_server.pid"

# Start the MCP server using the virtual environment
nohup mcp_env/bin/python mcp_server.py > mcp_server.log 2>&1 & echo $! > $PID_FILE

# Wait a bit for the server to start
sleep 2

# Check if the server is running
if [ -f "$PID_FILE" ] && ps -p $(cat $PID_FILE) > /dev/null; then
    echo "MCP server started successfully!"
    echo "MCP server running with PID: $(cat $PID_FILE)"
    echo "To connect with Claude, use the mcp address: localhost:7777"
    
    # Test the connection
    echo "Testing TUI connection..."
    python3 tui_connector.py test_connection
else
    echo "Failed to start MCP server. Check mcp_server.log for details."
fi