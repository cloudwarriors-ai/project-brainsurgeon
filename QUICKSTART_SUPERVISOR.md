# Quick Start: LLM Supervisor with TUI

This guide demonstrates how to use the LLM-based supervisor pattern to monitor and control TUI instances, similar to how we created a Flask hello-world application with monitoring and intervention.

## Setup

1. Connect to your TUI instances using the MCP bridge.
2. Use an LLM (like Claude) to create, monitor, and supervise tasks.

## Step-by-Step Guide

### 1. Set Up TUI Connections

```python
# Using an LLM, add TUI connections to monitor
opencode-bridge_add_connection(connection_id="tui-7777", url="http://localhost:7777")
opencode-bridge_add_connection(connection_id="tui-8888", url="http://localhost:8888")

# Set the active connection
opencode-bridge_set_active_connection(connection_id="tui-8888")
```

### 2. Create Task Tracking with Todos

```python
# Set up todo items to track progress
todowrite(todos=[
    {"content": "Create folder structure", "status": "pending", "priority": "high", "id": "1"},
    {"content": "Create a simple Flask app", "status": "pending", "priority": "high", "id": "2"},
    {"content": "Run the Flask application", "status": "pending", "priority": "high", "id": "3"},
    {"content": "Monitor agent progress", "status": "pending", "priority": "medium", "id": "4"},
    {"content": "Evaluate responses and summary", "status": "pending", "priority": "medium", "id": "5"}
])
```

### 3. Inject the Initial Prompt

```python
# Send a prompt to the TUI agent
opencode-bridge_tui_append_prompt(text="Create a folder named test666, and inside it set up a simple Flask hello-world application. Then run the application.")
opencode-bridge_tui_submit_prompt()

# Update the todo to reflect progress
todowrite(todos=[...first todo as in_progress...])
```

### 4. Monitor Progress and Responses

```python
# Get the session ID
sessions = opencode-bridge_tui_get_sessions()
session_id = sessions[0]["id"]  # Get the most recent session

# Get messages from that session
messages = opencode-bridge_tui_get_session_messages(session_id=session_id)

# Or use a Task agent to monitor
task(
    description="Monitor TUI messages",
    prompt="Monitor the messages in the TUI connection tui-8888 for responses to our request. Report back if there are issues.",
    subagent_type="general"
)
```

### 5. Analyze and Intervene When Needed

The LLM can analyze the messages and detect issues:

- Identify errors (like the Flask/Werkzeug compatibility issue we saw)
- Detect when the agent is stuck
- Provide guidance or follow-up prompts when needed

```python
# If an error is detected, inject a follow-up prompt
if "error" in messages:
    opencode-bridge_tui_append_prompt(text="Let's try specifying Werkzeug==2.0.1 in the requirements.txt file to fix the compatibility issue.")
    opencode-bridge_tui_submit_prompt()
```

### 6. Evaluate Results and Provide Summary

```python
# Mark todos as completed as progress is made
todowrite(todos=[...update todo statuses...])

# Provide a summary of the results
"Based on monitoring, the Flask application has been successfully created and is running on port 5000. The agent encountered a compatibility issue but fixed it by specifying Werkzeug 2.0.1 in the requirements.txt file."
```

## Real Example: Creating a Flask Hello-World App

Here's how we used the supervisor pattern to create and monitor a Flask application:

1. **Added TUI connections**:
   ```
   opencode-bridge_add_connection(connection_id="tui-7777", url="http://localhost:7777")
   opencode-bridge_add_connection(connection_id="tui-8888", url="http://localhost:8888")
   ```

2. **Created todo tracking**:
   ```
   todowrite(todos=[...tasks for creating and monitoring Flask app...])
   ```

3. **Injected prompt to create the Flask app**:
   ```
   opencode-bridge_tui_append_prompt(text="Create a folder named test666, and inside it set up a simple Flask hello-world application. Then run the application.")
   ```

4. **Monitored the agent's progress**:
   ```
   task(description="Monitor TUI messages", prompt="Monitor the messages in the TUI connection tui-8888...", subagent_type="general")
   ```

5. **Provided a summary of the results**:
   ```
   "Based on the monitoring, the Flask application has been successfully created and is now running on port 5000..."
   ```

## Tips for Effective Supervision

1. **Use Clear Initial Prompts**: Make your initial instructions clear and specific.

2. **Proactive Monitoring**: Don't wait for errors to be reported - actively check the progress.

3. **Timely Interventions**: When you detect an issue, provide guidance promptly.

4. **Track Progress with Todos**: Use the todo system to keep track of what has been done and what's next.

5. **Smart Analysis**: Let the LLM analyze messages to detect issues that might not be explicitly reported.

## Next Steps

- Create automated workflows for common tasks
- Develop patterns for handling specific types of errors
- Create a library of prompts for different scenarios