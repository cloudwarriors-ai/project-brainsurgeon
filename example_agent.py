#!/usr/bin/env python3
"""
Example Agent - Demonstrates how agents should publish events to our local bus
"""
import time
import uuid
from local_event_bus import publish_agent_start, publish_agent_progress, publish_agent_stop

class ExampleAgent:
    def __init__(self, task_description):
        self.agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        self.task = task_description
    
    def run_task(self):
        """Simulate running a task with event publishing"""
        print(f"🤖 Agent {self.agent_id} starting task: {self.task}")
        
        # Publish start event
        publish_agent_start(self.agent_id, self.task)
        
        try:
            # Simulate work with progress updates
            stages = [
                "Initializing task",
                "Processing data", 
                "Running analysis",
                "Generating results",
                "Finalizing output"
            ]
            
            for i, stage in enumerate(stages):
                progress = f"{stage} ({i+1}/{len(stages)})"
                print(f"  📋 {progress}")
                publish_agent_progress(self.agent_id, self.task, progress)
                time.sleep(2)  # Simulate work
            
            # Task completed successfully
            result = f"Task '{self.task}' completed successfully with 5 stages"
            print(f"  ✅ {result}")
            publish_agent_stop(self.agent_id, self.task, "completed", result)
            
        except Exception as e:
            # Task failed
            error_msg = f"Task failed: {str(e)}"
            print(f"  ❌ {error_msg}")
            publish_agent_stop(self.agent_id, self.task, "failed", error_msg)

def create_failing_agent():
    """Create an agent that will fail for testing"""
    agent_id = f"agent-{uuid.uuid4().hex[:8]}"
    task = "Intentionally failing task for testing"
    
    print(f"🤖 Agent {agent_id} starting task: {task}")
    publish_agent_start(agent_id, task)
    
    time.sleep(2)
    publish_agent_progress(agent_id, task, "Starting to fail...")
    
    time.sleep(2)
    error_msg = "Simulated failure for supervisor testing"
    publish_agent_stop(agent_id, task, "failed", error_msg)
    print(f"  ❌ {error_msg}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "fail":
        create_failing_agent()
    else:
        # Create and run a successful agent
        agent = ExampleAgent("Process user data and generate report")
        agent.run_task()