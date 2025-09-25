#!/bin/bash

# Start the Stop Event Supervisor
echo "Starting Stop Event Supervisor..."
echo "This will monitor for agent stop events and trigger intervention when needed"
echo "Press Ctrl+C to stop"

cd /root/code/project-brainsurgeon
python3 stop_event_supervisor.py