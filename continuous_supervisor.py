#!/usr/bin/env python3
import time
import subprocess
import json
from datetime import datetime

class ContinuousSupervisor:
    def __init__(self):
        self.restart_count = 0
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open("supervisor.log", "a") as f:
            f.write(log_msg + "\n")
    
    def start_supervisor_agent(self):
        """Start a new supervisor agent using the Task tool"""
        try:
            self.restart_count += 1
            self.log(f"Starting supervisor agent #{self.restart_count}")
            
            # Create a prompt that explicitly tells the agent to monitor continuously
            prompt = f"""SUPERVISOR AGENT #{self.restart_count} - CONTINUOUS MONITORING MODE

You are now the active supervisor monitoring all agents. 

Your instructions:
1. IMMEDIATELY start monitoring with opencode-bridge.get_next_event()
2. Check ALL sessions every 30 seconds using opencode-bridge_tui_get_sessions()  
3. Look for AI_APICallError, session failures, or inactive agents
4. When you find problems, restart those agents
5. Send a status toast every 2 minutes: "Supervisor #{self.restart_count} monitoring X agents"
6. NEVER STOP - if you encounter errors, handle them and continue monitoring
7. If you must stop, immediately restart yourself by calling this same continuous_supervisor.py

BEGIN CONTINUOUS MONITORING NOW."""

            # Use subprocess to start the task
            result = subprocess.run([
                "python3", "-c", 
                f"""
import subprocess
subprocess.run(['python3', '-c', '''
from task import task
task("Supervisor agent", "{prompt}", "supervisor")
'''])
"""
            ], capture_output=True, text=True, timeout=5)
            
            self.log(f"Supervisor agent #{self.restart_count} started")
            return True
            
        except Exception as e:
            self.log(f"Failed to start supervisor: {e}")
            return False
    
    def run_forever(self):
        """Run continuous supervisor monitoring"""
        self.log("Continuous Supervisor started - will restart agents that stop")
        
        while True:
            try:
                # Start a new supervisor agent
                self.start_supervisor_agent()
                
                # Wait for the agent to run for a while
                time.sleep(180)  # Let it run for 3 minutes
                
                self.log("Restarting supervisor agent (preventive restart)")
                
            except KeyboardInterrupt:
                self.log("Continuous supervisor stopped by user")
                break
            except Exception as e:
                self.log(f"Error in continuous supervisor: {e}")
                time.sleep(30)

if __name__ == "__main__":
    supervisor = ContinuousSupervisor()
    supervisor.run_forever()