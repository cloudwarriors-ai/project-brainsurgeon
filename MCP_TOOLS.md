# Opencode Bridge MCP Tools

This document provides comprehensive information about the custom MCP (Model Context Protocol) tools available in the `opencode-bridge` server. These tools allow programmatic interaction with the Opencode TUI (Terminal User Interface) and extend file system capabilities.

## Available Tools

All tools provided by the `opencode-bridge` MCP server use the prefix `opencode-bridge_` followed by the tool name.

### TUI Interaction Tools

These tools allow interaction with the Opencode TUI running on port 7777:

| Tool | Description | Parameters |
|------|-------------|------------|
| `opencode-bridge_tui_get_sessions` | Get a list of all sessions from the TUI API | None |
| `opencode-bridge_tui_get_session` | Get details about a specific session | `session_id`: The ID of the session to retrieve |
| `opencode-bridge_tui_get_session_messages` | Get all messages for a specific session | `session_id`: The ID of the session to retrieve messages for |
| `opencode-bridge_tui_get_config` | Get the TUI configuration | None |
| `opencode-bridge_tui_get_projects` | Get a list of all projects | None |
| `opencode-bridge_tui_get_current_project` | Get the current project | None |
| `opencode-bridge_tui_test_connection` | Test connection to the TUI API | `url` (optional): URL to test (default: http://localhost:7777)<br>`timeout` (optional): Timeout in seconds (default: 5) |
| `opencode-bridge_show_toast` | Show a toast notification in the TUI | `message`: Message to display<br>`variant` (optional): Type of toast (info, success, warning, error)<br>`title` (optional): Title for the toast |
| `opencode-bridge_tui_append_prompt` | Append text to the TUI prompt | `text`: Text to append to the prompt |
| `opencode-bridge_tui_submit_prompt` | Submit the current prompt in the TUI | None |

### File System Tools

These tools provide file system access capabilities:

| Tool | Description | Parameters |
|------|-------------|------------|
| `opencode-bridge_read_file` | Reads a file from the local filesystem | `filePath`: Path to the file<br>`offset` (optional): Line number to start reading from<br>`limit` (optional): Number of lines to read |
| `opencode-bridge_write_file` | Writes content to a file | `filePath`: Path to the file<br>`content`: Content to write |
| `opencode-bridge_edit_file` | Performs exact string replacements in files | `filePath`: Path to the file<br>`oldString`: Text to replace<br>`newString`: New text<br>`replaceAll` (optional): Whether to replace all occurrences |
| `opencode-bridge_glob_files` | Fast file pattern matching | `pattern`: Glob pattern to match<br>`path` (optional): Directory to search in |
| `opencode-bridge_grep_search` | Fast content search using regex | `pattern`: Regex pattern to search for<br>`path` (optional): Directory to search in<br>`include` (optional): File pattern to include |
| `opencode-bridge_list_dir` | Lists files and directories | `path`: Directory to list<br>`ignore` (optional): List of glob patterns to ignore |

### Other Tools

Additional utility tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `opencode-bridge_run_bash` | Executes a given bash command | `command`: The command to execute<br>`timeout` (optional): Timeout in milliseconds<br>`description`: Brief description of the command |
| `opencode-bridge_fetch_web` | Fetches content from a URL | `url`: URL to fetch<br>`format` (optional): Format to return (text, markdown, html)<br>`timeout` (optional): Timeout in seconds |
| `opencode-bridge_todowrite` | Create and manage a structured task list | `todos`: Array of todo items |
| `opencode-bridge_todoread` | Read the todo list | None |

## Example Usage

Here are examples of how to use these tools:

### Test TUI Connection

```python
# Test with default URL (http://localhost:7777)
result = await opencode-bridge_tui_test_connection()
# Returns connection status

# Test with custom URL and timeout
result = await opencode-bridge_tui_test_connection(url="http://localhost:7777/doc", timeout=10)
# Returns connection status for the specified URL with a 10-second timeout
```

### Get TUI Sessions

```python
result = await opencode-bridge_tui_get_sessions()
# Returns a list of all sessions
```

### Get Session Messages

```python
result = await opencode-bridge_tui_get_session_messages(session_id="ses_6890c3f31ffeMj1TowSO1g0haj")
# Returns all messages and conversation content for the specified session
```

### Show Toast Notification

```python
result = await opencode-bridge_show_toast(message="Hello from MCP!", variant="success", title="Test")
# Shows a success toast notification in the TUI
```

### Interact with TUI Prompt

```python
# Append text to the prompt
result = await opencode-bridge_tui_append_prompt(text="Write a poem about cats")

# Submit the prompt 
result = await opencode-bridge_tui_submit_prompt()
```

### Read a File

```python
result = await opencode-bridge_read_file(filePath="/path/to/file.txt")
# Returns the content of the file
```

### Search for Files

```python
result = await opencode-bridge_glob_files(pattern="**/*.py")
# Returns all Python files in the current directory and subdirectories
```

### Execute a Bash Command

```python
result = await opencode-bridge_run_bash(command="ls -la", description="List files in directory")
# Returns the output of the command
```

### Managing Todo Lists

```python
# Write todos
await opencode-bridge_todowrite(todos=[
    {"content": "Task 1", "status": "pending", "priority": "high", "id": "1"},
    {"content": "Task 2", "status": "completed", "priority": "medium", "id": "2"}
])

# Read todos
todos = await opencode-bridge_todoread()
```

## Initialization and Configuration

The `opencode-bridge` MCP server is configured in `opencode.json` and is started automatically when Opencode launches. The server connects to the TUI API running on port 7777.

To check if the server is running:

```bash
ps aux | grep "python mcp_server.py"
```

To manually start the server:

```bash
cd /root/code/project-brainsurgeon
./start_mcp_server.sh
```

## Troubleshooting

If you encounter issues with the `opencode-bridge` tools:

1. Check if the MCP server is running
2. Verify that the TUI API is accessible at http://localhost:7777/doc
3. Use the `opencode-bridge_tui_test_connection` tool to test connectivity:
   ```python
   result = await opencode-bridge_tui_test_connection()
   # Check if result["success"] is True
   ```
4. Check the MCP server logs in `mcp_server.log`
5. Restart the MCP server using `./start_mcp_server.sh`

## Development

To add new tools to the `opencode-bridge` MCP server, modify the `mcp_server.py` file. Each tool is defined using the `@app.tool()` decorator and should be async functions that return JSON-serializable responses.