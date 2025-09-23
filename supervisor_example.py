"""
Example of a supervisor pattern for TUI monitoring and prompt injection.
This demonstrates how to monitor TUI agents, inject prompts, and evaluate responses.
"""

import time
import json

class TUISupervisor:
    """Supervisor for TUI connections that can monitor and inject prompts."""
    
    def __init__(self):
        """Initialize the supervisor with empty connections and todos."""
        self.todos = []
        self.active_connection = None
        self.session_id = None
    
    def initialize_todos(self):
        """Set up the initial todos for task tracking."""
        self.todos = [
            {"content": "Create folder structure", "status": "pending", "priority": "high", "id": "1"},
            {"content": "Set up Flask application", "status": "pending", "priority": "high", "id": "2"},
            {"content": "Run the application", "status": "pending", "priority": "high", "id": "3"},
            {"content": "Monitor progress and inject prompts", "status": "pending", "priority": "medium", "id": "4"},
            {"content": "Evaluate responses and provide summary", "status": "pending", "priority": "medium", "id": "5"}
        ]
        return self.todos
    
    def update_todo(self, id, status):
        """Update the status of a todo item."""
        for todo in self.todos:
            if todo["id"] == id:
                todo["status"] = status
                break
        return self.todos
    
    def setup_connections(self):
        """Set up TUI connections for monitoring."""
        # In a real implementation, this would use the actual TUI connector
        print("Setting up TUI connections...")
        print("Added connection tui-7777 (http://localhost:7777)")
        print("Added connection tui-8888 (http://localhost:8888)")
        self.active_connection = "tui-8888"
        print(f"Set active connection to {self.active_connection}")
    
    def inject_prompt(self, prompt):
        """Inject a prompt to the active TUI connection."""
        print(f"Injecting prompt to {self.active_connection}: {prompt}")
        # In a real implementation, this would call the TUI connector's append_prompt and submit_prompt
        return True
    
    def get_session_messages(self):
        """Get the latest messages from the active session."""
        # In a real implementation, this would fetch actual messages
        # This is a simulation of messages that might be received
        return [
            {"role": "user", "text": "Create a folder named test666, and inside it set up a simple Flask hello-world application. Then run the application."},
            {"role": "assistant", "text": "I'll create a folder named test666 and set up a simple Flask hello-world application."},
            {"role": "assistant", "text": "Created folder test666"},
            {"role": "assistant", "text": "Created app.py with Flask hello-world code"},
            {"role": "assistant", "text": "Created requirements.txt with Flask dependencies"},
            {"role": "assistant", "text": "Error: compatibility issue between Flask 2.0.1 and the latest Werkzeug"},
            {"role": "assistant", "text": "Updated requirements.txt to specify compatible versions"},
            {"role": "assistant", "text": "Installed dependencies"},
            {"role": "assistant", "text": "Flask application is now running on http://192.168.100.13:5000/"}
        ]
    
    def evaluate_messages(self, messages):
        """Evaluate messages to determine progress and issues."""
        status = {
            "folder_created": False,
            "app_created": False,
            "requirements_created": False,
            "error_detected": False,
            "error_resolved": False,
            "app_running": False
        }
        
        for message in messages:
            text = message.get("text", "").lower()
            
            if "created folder test666" in text:
                status["folder_created"] = True
                self.update_todo("1", "completed")
            
            if "created app.py" in text:
                status["app_created"] = True
                
            if "created requirements.txt" in text:
                status["requirements_created"] = True
                
            if "error" in text:
                status["error_detected"] = True
                
            if "updated requirements.txt" in text:
                status["error_resolved"] = True
            
            if "flask application is now running" in text:
                status["app_running"] = True
                self.update_todo("3", "completed")
        
        if status["app_created"] and status["requirements_created"]:
            self.update_todo("2", "completed")
            
        if status["error_detected"] and not status["error_resolved"]:
            # If there's an error that hasn't been resolved, we could inject a prompt
            self.inject_prompt("Try specifying Werkzeug==2.0.1 in your requirements.txt")
            
        return status
    
    def run_supervisor_loop(self):
        """Run the main supervisor loop."""
        self.initialize_todos()
        self.setup_connections()
        
        # Update todos to reflect our progress
        self.update_todo("4", "in_progress")
        
        # Inject the initial prompt
        initial_prompt = "Create a folder named test666, and inside it set up a simple Flask hello-world application. Then run the application."
        self.inject_prompt(initial_prompt)
        
        # Simulate monitoring loop
        print("\nStarting monitoring loop...")
        print("Getting session messages...")
        messages = self.get_session_messages()
        
        # Evaluate the messages
        print("Evaluating messages...")
        status = self.evaluate_messages(messages)
        
        # Update todos based on evaluation
        self.update_todo("4", "completed")
        self.update_todo("5", "in_progress")
        
        # Generate a summary
        print("\nGenerating summary of the TUI agent's progress:")
        print("=================================================")
        print(f"Folder created: {status['folder_created']}")
        print(f"Flask app created: {status['app_created']}")
        print(f"Requirements created: {status['requirements_created']}")
        print(f"Error detected: {status['error_detected']}")
        print(f"Error resolved: {status['error_resolved']}")
        print(f"App running: {status['app_running']}")
        print("=================================================")
        
        # Mark the final todo as completed
        self.update_todo("5", "completed")
        
        # Print final todo status
        print("\nFinal todo status:")
        for todo in self.todos:
            print(f"{todo['id']}. {todo['content']} - {todo['status']}")

if __name__ == "__main__":
    supervisor = TUISupervisor()
    supervisor.run_supervisor_loop()