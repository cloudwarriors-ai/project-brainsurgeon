#!/usr/bin/env python3
"""
Stop Event Supervisor - Monitors only for stop events from remote agents
When a stop event is detected, triggers the supervisor to interact with the agent
"""
import time
import json
import requests
import subprocess
from datetime import datetime

class StopEventSupervisor:
    def __init__(self, tui_url="http://localhost:44907"):
        self.tui_url = tui_url
        self.event_store = {}
        self.last_check = time.time()
        
    def log(self, message):
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open("stop_event_supervisor.log", "a") as f:
            f.write(log_msg + "\n")
    
    def get_next_event(self):
        """Get next event and store in dict, return last message if stop event detected"""
        try:
            # Make direct API call to next-event endpoint (404 is expected, just triggers update)
            try:
                response = requests.get(f"{self.tui_url}/next-event", timeout=5)
                self.log(f"next-event call status: {response.status_code}")
            except Exception as e:
                self.log(f"next-event call failed (expected): {e}")
            
            # Get sessions regardless of next-event result
            sessions_response = requests.get(f"{self.tui_url}/session", timeout=10)
            
            # Now get sessions to find most recent one
            if sessions_response.status_code == 200:

                
                sessions = sessions_response.json()
                if not sessions:
                    return None
                
                # Find most recent session
                most_recent_session = max(sessions, key=lambda s: s.get("time", {}).get("updated", 0))
                session_id = most_recent_session.get("id")
                
                if not session_id:
                    return None
                
                # Get messages from the most recent session
                messages_response = requests.get(f"{self.tui_url}/session/{session_id}/message", timeout=10)
                if messages_response.status_code != 200:
                    return None
                
                messages_data = messages_response.json()
                if isinstance(messages_data, list):
                    messages = messages_data
                else:
                    messages = messages_data.get("messages", [])
                if not messages:
                    return None
                
                # Return data structure
                data = {
                    "session_id": session_id,
                    "session_title": most_recent_session.get("title", ""),
                    "last_message": messages[-1],
                    "total_messages": len(messages)
                }
                
                # Store the event data
                current_time = time.time()
                self.event_store[current_time] = data
                
                # Clean old events (keep only last 100)
                if len(self.event_store) > 100:
                    old_keys = sorted(self.event_store.keys())[:-100]
                    for key in old_keys:
                        del self.event_store[key]
                
                return data
            else:
                return None

                
        except Exception as e:
            self.log(f"Error getting next event: {e}")
            return None
    
    def is_stop_event(self, event_data):
        """Check if this is a stop event from an agent"""
        if not event_data or "error" in event_data:
            return False
        
        last_message = event_data.get("last_message", {})
        if not last_message:
            return False
        
        # Handle different message structures
        message_info = last_message.get("info", last_message)
        content = ""
        role = message_info.get("role", "")
        
        # Extract content from different possible locations
        if "content" in message_info:
            content = str(message_info["content"]).lower()
        elif "text" in message_info:
            content = str(message_info["text"]).lower()
        elif isinstance(message_info.get("system"), list):
            # Join system messages if it's a list
            content = " ".join(message_info["system"]).lower()
        
        self.log(f"Checking message: role={role}, content_length={len(content)}, content_preview={content[:100]}...")
        
        # Look for stop indicators in assistant messages
        # But ignore very long system messages (likely agent instructions)
        if role == "assistant" and len(content) < 5000:  # Skip very long system messages
            stop_indicators = [
                "task completed",
                "task done", 
                "finished working on",
                "work is complete",
                "stopping now",
                "done with this task",
                "task finished",
                "implementation complete",
                "all done"
            ]
            
            for indicator in stop_indicators:
                if indicator in content:
                    self.log(f"Stop indicator found: '{indicator}'")
                    return True
        elif len(content) >= 5000:
            self.log(f"Skipping very long message ({len(content)} chars) - likely system message")
        
        return False
    
    def trigger_supervisor(self, event_data):
        """Trigger supervisor to interact with the stopped agent"""
        try:
            session_id = event_data.get("session_id")
            last_message = event_data.get("last_message", {})
            
            self.log(f"Stop event detected in session {session_id}")
            
            # Create a prompt for the supervisor to handle this stopped agent
            supervisor_prompt = f"""
STOP EVENT DETECTED - SUPERVISOR INTERVENTION REQUIRED

Session ID: {session_id}
Last message from agent: {last_message.get('content', 'N/A')}
Last message role: {last_message.get('role', 'N/A')}

Your task:
1. Get the full context of this session using tui_get_session_messages
2. Analyze what the agent was working on and why it stopped
3. Determine if the task was completed or if intervention is needed
4. If task incomplete, provide guidance or restart the agent with updated instructions
5. Send a toast notification summarizing the situation

Use the session ID provided to get full context before taking action.
"""
            
            # Start supervisor agent with this specific task
            cmd = [
                "python3", "-c", 
                f"""
import subprocess
import json

# Simulate calling the Task tool to start supervisor
prompt = '''{supervisor_prompt}'''

print("Starting supervisor to handle stop event...")
print("Session ID:", "{session_id}")
print("Supervisor will analyze and take appropriate action")
                """
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            self.log(f"Supervisor triggered for session {session_id}")
            
            return True
            
        except Exception as e:
            self.log(f"Error triggering supervisor: {e}")
            return False
    
    def run(self):
        """Main monitoring loop - only watch for stop events"""
        self.log("Stop Event Supervisor started - monitoring for agent stop events...")
        self.log(f"Monitoring TUI at: {self.tui_url}")
        
        while True:
            try:
                self.log("Checking for events...")
                # Get next event and check for stop events
                event_data = self.get_next_event()
                
                if event_data:
                    self.log(f"Got event from session: {event_data.get('session_id')} - {event_data.get('session_title')}")
                    if self.is_stop_event(event_data):
                        self.log("🚨 STOP EVENT DETECTED! Triggering supervisor...")
                        self.trigger_supervisor(event_data)
                    else:
                        self.log("ℹ Event is not a stop event, continuing monitoring...")
                else:
                    self.log("No event data received")
                
                # Wait between checks (lighter monitoring)
                self.log("Waiting 10 seconds before next check...")
                time.sleep(10)
                
            except KeyboardInterrupt:
                self.log("Stop Event Supervisor stopped by user")
                break
            except Exception as e:
                self.log(f"Error in monitoring loop: {e}")
                time.sleep(30)

if __name__ == "__main__":
    supervisor = StopEventSupervisor()
    supervisor.run()