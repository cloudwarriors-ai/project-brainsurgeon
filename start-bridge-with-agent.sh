#!/bin/bash
# Script to start the Opencode Bridge with event forwarding to a mock agent

# Load environment variables
set -a
source .env
set +a

# Make sure the Python virtual environment exists
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install fastmcp httpx

# Start the mock agent server in the background
echo "Starting mock agent server on port 3000..."
node test-event-forwarder.js &
AGENT_PID=$!

# Function to clean up on exit
cleanup() {
  echo "Shutting down..."
  kill $AGENT_PID
  exit 0
}

# Set up trap for clean shutdown
trap cleanup INT TERM

# Start the MCP server
echo "Starting Opencode Bridge MCP server..."
python mcp_server.py

# This should not be reached normally, but just in case
cleanup