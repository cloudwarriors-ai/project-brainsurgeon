#!/usr/bin/env python3
"""
TUI-driven Supervisor
Uses the opencode-bridge TUI commands to monitor and restart agents
"""
import sys
import os
import time
import subprocess
import json
from datetime import datetime

# Add current directory to path to import MCP modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

class TUISupervisor:
    def __init__(self):
        self.project_name = "project-brainsurgeon"
        self.connection_id = None
        self.last_session_count = 0
        self.restart_count = 0
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open("supervisor_tui.log", "a") as f:
            f.write(log_msg + "\n")
    
    def run_mcp_command(self, tool_name, **kwargs):
        """Run an MCP command using the opencode-bridge"""
        try:
            # Build the command
            cmd = ["python3", "-c", f"""
import sys
sys.path.append('{current_dir}')
from mcp_server import run_tool
result = run_tool('{tool_name}', {json.dumps(kwargs)})
print(result)
"""]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return json.loads(result.stdout.strip()) if result.stdout.strip() else None
            else:
                self.log(f"MCP command failed: {result.stderr}")
                return None
        except Exception as e:
            self.log(f"Error running MCP command {tool_name}: {e}")
            return None
    
    def find_project_connection(self):
        """Find the TUI connection for project-brainsurgeon"""
        connections = self.run_mcp_command("opencode-bridge_list_connections")
        if not connections:
            self.log("No connections found")
            return None
            
        # Look for project-brainsurgeon connection
        for conn in connections.get("connections", []):
            if "project-brainsurgeon" in conn.get("project_name", "").lower():
                self.connection_id = conn.get("connection_id")
                self.log(f"Found project connection: {self.connection_id} on {conn.get('url')}")
                return self.connection_id
        
        # If not found, look for any active connection
        active_conn = connections.get("active_connection")
        if active_conn:
            self.connection_id = active_conn
            self.log(f"Using active connection: {self.connection_id}")
            return self.connection_id
            
        self.log("No suitable connection found")
        return None
    
    def get_sessions(self):
        """Get all sessions from the TUI"""
        sessions = self.run_mcp_command("opencode-bridge_tui_get_sessions", 
                                      connection_id=self.connection_id)
        return sessions if sessions else []
    
    def send_toast(self, message, title="TUI Supervisor", variant="info"):
        """Send a toast notification"""
        return self.run_mcp_command("opencode-bridge_show_toast",
                                  connection_id=self.connection_id,
                                  message=message,
                                  title=title,
                                  variant=variant)
    
    def append_and_submit_prompt(self, prompt):
        """Send a prompt to the TUI"""
        # Append the prompt
        append_result = self.run_mcp_command("opencode-bridge_tui_append_prompt",
                                           connection_id=self.connection_id,
                                           text=prompt)
        if not append_result:
            return False
            
        # Submit the prompt
        submit_result = self.run_mcp_command("opencode-bridge_tui_submit_prompt",
                                           connection_id=self.connection_id)
        return bool(submit_result)
    
    def start_supervisor_agent(self):
        """Start a new supervisor agent via TUI prompt"""
        self.restart_count += 1
        
        prompt = f"""Start a continuous agent supervisor (restart #{self.restart_count}).

Use the Task tool to launch a 'supervisor' subagent with this prompt:

"You are Supervisor Agent #{self.restart_count}. Monitor all active sessions continuously:

1. Use opencode-bridge.get_next_event() every 30 seconds
2. Check for AI_APICallError, session failures, or inactive agents  
3. When problems found, restart affected agents immediately
4. Send toast notification every 2 minutes: 'Supervisor #{self.restart_count} monitoring X sessions'
5. Never stop monitoring - handle all errors and continue
6. If you encounter any issues, immediately call this same supervisor script

BEGIN CONTINUOUS MONITORING NOW."

Start this supervisor agent immediately."""

        success = self.append_and_submit_prompt(prompt)
        if success:
            self.log(f"Started supervisor agent #{self.restart_count}")
            self.send_toast(f"Supervisor agent #{self.restart_count} started via TUI", 
                          "Supervisor", "success")
        else:
            self.log(f"Failed to start supervisor agent #{self.restart_count}")
        
        return success
    
    def monitor_and_restart(self):
        """Main monitoring loop"""
        self.log("TUI Supervisor starting...")
        
        # Find the connection
        if not self.find_project_connection():
            self.log("Could not find TUI connection - exiting")
            return
        
        # Send initial notification
        self.send_toast("TUI Supervisor started - will monitor and restart agents", 
                       "TUI Supervisor", "info")
        
        # Start initial supervisor agent
        self.start_supervisor_agent()
        
        check_count = 0
        while True:
            try:
                check_count += 1
                
                # Get current sessions
                sessions = self.get_sessions()
                session_count = len(sessions) if sessions else 0
                
                self.log(f"Check #{check_count}: {session_count} sessions active")
                
                # Check if we need to restart supervisor
                if session_count != self.last_session_count:
                    self.log(f"Session count changed from {self.last_session_count} to {session_count}")
                    self.last_session_count = session_count
                
                # Every 10 checks (5 minutes), restart supervisor preventively
                if check_count % 10 == 0:
                    self.log("Preventive supervisor restart")
                    self.start_supervisor_agent()
                
                # Every 4 checks (2 minutes), send status
                if check_count % 4 == 0:
                    self.send_toast(f"TUI Supervisor active: monitoring {session_count} sessions", 
                                  "Supervisor Status", "info")
                
                time.sleep(30)
                
            except KeyboardInterrupt:
                self.log("TUI Supervisor stopped by user")
                self.send_toast("TUI Supervisor stopped", "Supervisor", "warning")
                break
            except Exception as e:
                self.log(f"Error in supervisor loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    supervisor = TUISupervisor()
    supervisor.monitor_and_restart()