# Multi-Connection TUI Management Guide

The OpenCode Bridge MCP server now supports connecting to and managing multiple TUI instances simultaneously. This allows you to work with multiple OpenCode projects at once.

## Overview

The multi-connection system provides:
- **Connection Registry**: Store and manage multiple TUI connections
- **Project-based Identification**: Identify connections by project name or custom ID
- **Active Connection Management**: Set which connection to use by default
- **Per-command Targeting**: Override the active connection for specific commands

## Connection Management Functions

### Adding Connections

```python
# Add a new connection
await add_connection(
    connection_id="my-project",
    url="http://localhost:7777", 
    project_name="My Project",
    description="Main development environment"
)
```

**Parameters:**
- `connection_id` (required): Unique identifier for this connection
- `url` (required): The TUI API endpoint URL
- `project_name` (optional): Human-readable project name (auto-detected if not provided)
- `description` (optional): Description of this connection

### Listing Connections

```python
# Get all registered connections
connections = await list_connections()

# Returns:
{
    "connections": [
        {
            "connection_id": "my-project",
            "url": "http://localhost:7777",
            "project_name": "My Project", 
            "description": "Main development environment",
            "is_active": true
        }
    ],
    "active_connection": "my-project",
    "default_url": "http://localhost:7777"
}
```

### Setting Active Connection

```python
# Set which connection to use by default
await set_active_connection("my-project")

# Clear active connection (use default)
await set_active_connection(None)
```

### Getting Connection Info

```python
# Get detailed info about a specific connection
info = await get_connection_info("my-project")

# Returns connection details plus current status (online/offline)
```

### Removing Connections

```python
# Remove a connection from the registry
await remove_connection("my-project")
```

## Using TUI Functions with Multiple Connections

All TUI-related functions now accept an optional `connection_id` parameter:

### Method 1: Use Active Connection
```python
# Set active connection once
await set_active_connection("project1")

# All subsequent calls use "project1"
sessions = await tui_get_sessions()
await show_toast("Hello from project1!")
```

### Method 2: Per-Command Targeting
```python
# Target specific connections per command
sessions1 = await tui_get_sessions(connection_id="project1")
sessions2 = await tui_get_sessions(connection_id="project2")

await show_toast("Hello!", connection_id="project1")
await show_toast("Hi there!", connection_id="project2")
```

### Method 3: Mixed Approach
```python
# Set default, but override when needed
await set_active_connection("project1")

sessions = await tui_get_sessions()  # Uses project1
await show_toast("Main project message")  # Uses project1

# Override for specific command
await show_toast("Secondary message", connection_id="project2")  # Uses project2
```

## Supported TUI Functions

All the following functions support the `connection_id` parameter:

- `tui_get_sessions(connection_id=None)`
- `tui_get_session(session_id, connection_id=None)` 
- `tui_get_config(connection_id=None)`
- `tui_get_projects(connection_id=None)`
- `tui_get_current_project(connection_id=None)`
- `show_toast(message, variant="info", title=None, connection_id=None)`
- `tui_append_prompt(text, connection_id=None)`
- `tui_submit_prompt(connection_id=None)`
- `tui_get_session_messages(session_id, connection_id=None)`

## Example Workflow

Here's a complete example of managing multiple OpenCode projects:

```python
# 1. Add connections for different projects
await add_connection("web-app", "http://localhost:7777", "Web Application")
await add_connection("api-server", "http://localhost:8888", "API Server") 
await add_connection("mobile-app", "http://localhost:9999", "Mobile App")

# 2. List all connections to verify
connections = await list_connections()
print(f"Registered {len(connections['connections'])} connections")

# 3. Set primary working connection
await set_active_connection("web-app")

# 4. Work with the active connection (web-app)
await show_toast("Starting development session")
sessions = await tui_get_sessions()

# 5. Check on other projects without switching active connection
api_sessions = await tui_get_sessions(connection_id="api-server")
mobile_project = await tui_get_current_project(connection_id="mobile-app")

# 6. Send notifications to all projects
for conn in connections["connections"]:
    await show_toast("Daily standup in 5 minutes!", connection_id=conn["connection_id"])

# 7. Switch to different project for focused work
await set_active_connection("api-server")
await tui_append_prompt("Review the latest API changes")
await tui_submit_prompt()
```

## Connection Status Monitoring

The system automatically tests connections when adding them and provides status information:

```python
# Get connection status
info = await get_connection_info("my-project")
print(f"Connection status: {info['status']}")  # "online" or "offline"
```

## Error Handling

- **Connection not found**: Functions return `{"error": "Connection 'id' not found"}`
- **Connection failed**: Functions return connection errors from the target TUI
- **Invalid URLs**: Connection tests fail during `add_connection`

## Best Practices

1. **Use descriptive connection IDs**: Choose IDs that clearly identify the project
2. **Set active connection**: Reduce the need to specify `connection_id` repeatedly
3. **Monitor connection status**: Check connection health before important operations
4. **Clean up unused connections**: Remove connections that are no longer needed
5. **Document your setup**: Keep track of which ports/URLs are used for which projects

## Migration from Single Connection

Existing code continues to work without changes. The system falls back to:
1. Active connection (if set)
2. Default URL (http://localhost:7777)

To migrate to multi-connection:
1. Add your connections using `add_connection`
2. Optionally set an active connection
3. Add `connection_id` parameters where needed