#!/usr/bin/env python3
"""
Local Event Supervisor - Monitors our own local agent events
Watches the local event bus for agent stop events
"""
import time
import json
from datetime import datetime
from local_event_bus import event_bus

class LocalEventSupervisor:
    def __init__(self):
        self.last_check = time.time()
        self.processed_events = set()
        
    def log(self, message):
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open("local_event_supervisor.log", "a") as f:
            f.write(log_msg + "\n")
    
    def process_stop_event(self, event):
        """Process a stop event from a local agent"""
        agent_id = event['agent_id']
        data = event['data']
        task = data.get('task', 'Unknown task')
        status = data.get('status', 'unknown')
        result = data.get('result', '')
        
        self.log(f"🚨 AGENT STOP EVENT: {agent_id}")
        self.log(f"  Task: {task}")
        self.log(f"  Status: {status}")
        if result:
            self.log(f"  Result: {result}")
        
        # Trigger supervisor action based on status
        if status == "completed":
            self.handle_completed_agent(agent_id, task, result)
        elif status == "failed":
            self.handle_failed_agent(agent_id, task, result)
        elif status == "cancelled":
            self.handle_cancelled_agent(agent_id, task, result)
    
    def handle_completed_agent(self, agent_id, task, result):
        """Handle successfully completed agent"""
        self.log(f"✅ Agent {agent_id} completed successfully")
        
        # Here you could:
        # - Archive results
        # - Trigger next steps in a workflow
        # - Send notifications
        # - Update status dashboards
        
        # For now, just log and continue
        self.log(f"📋 Completed task logged: {task}")
    
    def handle_failed_agent(self, agent_id, task, result):
        """Handle failed agent"""
        self.log(f"❌ Agent {agent_id} failed")
        
        # Here you could:
        # - Retry the task
        # - Alert administrators
        # - Start recovery procedures
        # - Log errors for analysis
        
        self.log(f"🔧 Failed task needs attention: {task}")
        if result:
            self.log(f"🔍 Failure reason: {result}")
    
    def handle_cancelled_agent(self, agent_id, task, result):
        """Handle cancelled agent"""
        self.log(f"⏸️ Agent {agent_id} was cancelled")
        
        # Here you could:
        # - Clean up resources
        # - Update workflow status
        # - Reschedule if needed
        
        self.log(f"🗑️ Cancelled task cleanup: {task}")
    
    def check_for_events(self):
        """Check for new events since last check"""
        # Get ALL events from event bus (not just since last check for debugging)
        all_events = event_bus.get_events()
        recent_events = event_bus.get_events(since=self.last_check)
        
        self.log(f"🔍 EVENT CHECK: Total events in bus: {len(all_events)}, New since last check: {len(recent_events)}")
        
        # Log summary of all events for debugging
        if all_events:
            event_types = {}
            for event in all_events:
                event_type = event.get('event_type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            self.log(f"📊 EVENT SUMMARY: {dict(event_types)}")
            
            # Log last 5 events for debugging
            self.log("📋 LAST 5 EVENTS:")
            for event in all_events[-5:]:
                self.log(f"    [{event.get('datetime', 'no-time')}] {event.get('event_type', 'no-type')}: {event.get('agent_id', 'no-id')} - {event.get('data', {})}")
        
        if recent_events:
            self.log(f"🆕 PROCESSING {len(recent_events)} NEW EVENTS:")
        
        for event in recent_events:
            event_id = f"{event['timestamp']}_{event['agent_id']}_{event['event_type']}"
            
            # Skip if already processed
            if event_id in self.processed_events:
                self.log(f"⏭️ SKIPPING already processed event: {event_id}")
                continue
            
            self.processed_events.add(event_id)
            self.log(f"🆕 NEW EVENT: {event['event_type']} from {event['agent_id']}")
            self.log(f"    Data: {event['data']}")
            self.log(f"    Time: {event.get('datetime', 'no-time')}")
            
            # Process stop events specially
            if event['event_type'] == 'agent_stop':
                self.log(f"🚨 PROCESSING STOP EVENT: {event['agent_id']}")
                self.process_stop_event(event)
            else:
                # Log all other events for full visibility
                self.log(f"ℹ️ NON-STOP EVENT: {event['event_type']} from {event['agent_id']}")
        
        # Update last check time
        self.last_check = time.time()
        self.log(f"⏰ Updated last_check to: {self.last_check}")
        
        # Clean up old processed events (keep last 1000)
        if len(self.processed_events) > 1000:
            # Convert to list, sort, and keep recent ones
            sorted_events = sorted(list(self.processed_events))
            self.processed_events = set(sorted_events[-1000:])
    
    def run(self):
        """Main monitoring loop"""
        self.log("Local Event Supervisor started - monitoring local agent events...")
        
        while True:
            try:
                self.check_for_events()
                
                # Clean old events from bus periodically
                if int(time.time()) % 3600 == 0:  # Every hour
                    event_bus.clear_old_events(max_age_hours=24)
                    self.log("🧹 Cleaned old events from bus")
                
                # Wait before next check
                time.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                self.log("Local Event Supervisor stopped by user")
                break
            except Exception as e:
                self.log(f"Error in monitoring loop: {e}")
                time.sleep(10)

if __name__ == "__main__":
    supervisor = LocalEventSupervisor()
    supervisor.run()