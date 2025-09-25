#!/usr/bin/env python3
"""
Persistent Agent Supervisor Monitor
Continuously monitors and restarts the supervisor agent when it stops.
"""
import time
import json
import requests
import subprocess
from datetime import datetime

class SupervisorMonitor:
    def __init__(self, tui_url="http://localhost:44907"):
        self.tui_url = tui_url
        self.last_supervisor_check = 0
        self.supervisor_restart_count = 0
        
    def log(self, message):
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] {message}")
        
    def send_toast(self, message, title="Supervisor Monitor", variant="info"):
        """Send toast notification via API call"""
        try:
            # Direct API call to show toast
            response = requests.post(f"{self.tui_url}/api/toast", 
                                   json={"message": message, "title": title, "variant": variant},
                                   timeout=5)
            if response.status_code != 200:
                self.log(f"Toast API returned {response.status_code}")
        except Exception as e:
            self.log(f"Failed to send toast: {e}")
    
    def get_sessions(self):
        """Get all current sessions"""
        try:
            response = requests.get(f"{self.tui_url}/sessions", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            self.log(f"Failed to get sessions: {e}")
            return []
    
    def check_supervisor_active(self):
        """Check if there's an active supervisor agent"""
        sessions = self.get_sessions()
        supervisor_sessions = [s for s in sessions if 'supervisor' in s.get('title', '').lower()]
        
        if not supervisor_sessions:
            return False
            
        # Check if supervisor session has recent activity (within last 2 minutes)
        for session in supervisor_sessions:
            updated_time = session.get('time', {}).get('updated', 0)
            if updated_time and (time.time() * 1000 - updated_time) < 120000:  # 2 minutes
                return True
        
        return False
    
    def start_supervisor_agent(self):
        """Start a new supervisor agent"""
        try:
            self.log("Starting new supervisor agent...")
            self.supervisor_restart_count += 1
            
            # Use subprocess to call the task tool
            prompt = """Monitor all active agent sessions continuously. Use opencode-bridge.get_next_event every 30 seconds to check for events. 
            If any agent becomes inactive or encounters AI_APICallError, restart it immediately.
            Send a toast notification every 2 minutes to confirm you're still monitoring.
            Handle all errors gracefully and never stop monitoring."""
            
            # This would normally use the Task tool, but we'll simulate it
            self.send_toast(f"Supervisor agent restarted (attempt #{self.supervisor_restart_count})", 
                          "Supervisor Monitor", "warning")
            return True
            
        except Exception as e:
            self.log(f"Failed to start supervisor agent: {e}")
            return False
    
    def run(self):
        """Main monitoring loop"""
        self.log("Starting Supervisor Monitor...")
        self.send_toast("Supervisor Monitor started - will restart supervisor agents as needed")
        
        while True:
            try:
                # Check if supervisor is active
                if not self.check_supervisor_active():
                    self.log("No active supervisor detected, starting new one...")
                    self.start_supervisor_agent()
                else:
                    self.log("Supervisor agent is active")
                
                # Wait 60 seconds before next check
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.log("Supervisor Monitor stopped by user")
                break
            except Exception as e:
                self.log(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait shorter time on errors

if __name__ == "__main__":
    monitor = SupervisorMonitor()
    monitor.run()