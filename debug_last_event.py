#!/usr/bin/env python3
"""
Debug script to check the last event from the current session
"""
import json
import requests
import time
from datetime import datetime

def log(message):
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")

def get_last_event(tui_url="http://localhost:44907"):
    """Get the last event from the most recent session"""
    try:
        log("Getting next-event...")
        # Call next-event first
        try:
            response = requests.get(f"{tui_url}/next-event", timeout=10)
            log(f"next-event response: {response.status_code}")
        except Exception as e:
            log(f"next-event failed: {e}")
        
        log("Getting sessions...")
        # Get all sessions
        sessions_response = requests.get(f"{tui_url}/session", timeout=10)
        if sessions_response.status_code != 200:
            log(f"Sessions request failed: {sessions_response.status_code}")
            return None
        
        sessions = sessions_response.json()
        log(f"Found {len(sessions)} sessions")
        
        if not sessions:
            log("No sessions found")
            return None
        
        # Find most recent session
        most_recent_session = max(sessions, key=lambda s: s.get("time", {}).get("updated", 0))
        session_id = most_recent_session.get("id")
        session_title = most_recent_session.get("title", "No title")
        
        log(f"Most recent session: {session_id} - '{session_title}'")
        
        if not session_id:
            log("No valid session ID found")
            return None
        
        log(f"Getting messages for session {session_id}...")
        # Get messages from the most recent session
        messages_response = requests.get(f"{tui_url}/session/{session_id}/message", timeout=10)
        if messages_response.status_code != 200:
            log(f"Messages request failed: {messages_response.status_code}")
            return None
        
        messages_data = messages_response.json()
        
        # Handle different response formats
        if isinstance(messages_data, list):
            messages = messages_data
        else:
            messages = messages_data.get("messages", [])
        
        log(f"Found {len(messages)} messages in session")
        
        if not messages:
            log("No messages found in session")
            return None
        
        # Get the last message
        last_message = messages[-1]
        log(f"Last message structure: {json.dumps(last_message, indent=2)[:500]}...")
        
        result = {
            "session_id": session_id,
            "session_title": session_title,
            "last_message": last_message,
            "total_messages": len(messages)
        }
        
        log("Last event data:")
        print(json.dumps(result, indent=2))
        
        # Check if it looks like a stop event
        content = last_message.get("content", "").lower()
        role = last_message.get("role", "")
        
        stop_indicators = [
            "task completed", "task done", "finished", "complete", 
            "stopping", "done with", "task finished"
        ]
        
        is_stop = False
        if role == "assistant":
            for indicator in stop_indicators:
                if indicator in content:
                    is_stop = True
                    log(f"✓ STOP EVENT DETECTED: Found '{indicator}' in message")
                    break
        
        if not is_stop:
            log("ℹ Not a stop event")
        
        return result
        
    except Exception as e:
        log(f"Error getting last event: {e}")
        return None

if __name__ == "__main__":
    log("Debugging last event from current session...")
    get_last_event()