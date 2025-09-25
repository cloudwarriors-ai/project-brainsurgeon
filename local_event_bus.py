#!/usr/bin/env python3
"""
Local Event Bus for monitoring our own agents
Simple file-based event system for agent stop events
"""
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

class LocalEventBus:
    def __init__(self, event_file="/tmp/agent_events.jsonl"):
        self.event_file = event_file
        self.ensure_event_file()
    
    def ensure_event_file(self):
        """Ensure event file exists"""
        if not os.path.exists(self.event_file):
            with open(self.event_file, 'w') as f:
                pass  # Create empty file
    
    def publish_event(self, event_type: str, agent_id: str, data: Dict[str, Any]):
        """Publish an event to the bus"""
        event = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "data": data
        }
        
        # Append to JSONL file
        with open(self.event_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def get_events(self, since: float = None, event_type: str = None) -> List[Dict[str, Any]]:
        """Get events from the bus"""
        events = []
        
        if not os.path.exists(self.event_file):
            return events
        
        try:
            with open(self.event_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        event = json.loads(line)
                        
                        # Filter by timestamp if provided
                        if since and event.get('timestamp', 0) <= since:
                            continue
                        
                        # Filter by event type if provided
                        if event_type and event.get('event_type') != event_type:
                            continue
                        
                        events.append(event)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return events
    
    def get_latest_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the latest N events"""
        events = self.get_events()
        return events[-count:] if events else []
    
    def clear_old_events(self, max_age_hours: int = 24):
        """Clear events older than max_age_hours"""
        cutoff = time.time() - (max_age_hours * 3600)
        
        if not os.path.exists(self.event_file):
            return
        
        # Read all events
        events = []
        with open(self.event_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    if event.get('timestamp', 0) > cutoff:
                        events.append(event)
                except json.JSONDecodeError:
                    continue
        
        # Rewrite file with recent events
        with open(self.event_file, 'w') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')

# Global event bus instance
event_bus = LocalEventBus()

def publish_agent_start(agent_id: str, task: str):
    """Publish agent start event"""
    event_bus.publish_event("agent_start", agent_id, {
        "task": task,
        "status": "started"
    })

def publish_agent_stop(agent_id: str, task: str, status: str, result: str = None):
    """Publish agent stop event"""
    event_bus.publish_event("agent_stop", agent_id, {
        "task": task,
        "status": status,  # "completed", "failed", "cancelled"
        "result": result
    })

def publish_agent_progress(agent_id: str, task: str, progress: str):
    """Publish agent progress event"""
    event_bus.publish_event("agent_progress", agent_id, {
        "task": task,
        "progress": progress
    })

if __name__ == "__main__":
    # Test the event bus
    print("Testing Local Event Bus...")
    
    # Publish some test events
    publish_agent_start("test-agent-1", "Test task implementation")
    publish_agent_progress("test-agent-1", "Test task implementation", "50% complete")
    publish_agent_stop("test-agent-1", "Test task implementation", "completed", "Task successfully implemented")
    
    # Read events
    print("\nLatest events:")
    events = event_bus.get_latest_events(5)
    for event in events:
        print(f"[{event['datetime']}] {event['event_type']}: {event['agent_id']} - {event['data']}")
    
    print("\nStop events only:")
    stop_events = event_bus.get_events(event_type="agent_stop")
    for event in stop_events:
        print(f"[{event['datetime']}] {event['agent_id']} stopped: {event['data']['status']}")