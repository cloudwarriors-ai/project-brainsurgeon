# Opencode Bridge MCP Tools

This project provides a set of custom MCP (Model Context Protocol) tools through the `opencode-bridge` server that allow AI assistants to interact with the Opencode TUI (Terminal User Interface) and perform various operations.

## Available Tools

All tools provided by the `opencode-bridge` MCP server use the prefix `opencode-bridge_` followed by the tool name.

To use these tools in your conversations with AI assistants, you must use the following format:

```
<function_calls>
<invoke name="opencode-bridge_TOOL_NAME">
<parameter name="PARAMETER_NAME">PARAMETER_VALUE</parameter>
</invoke>
</function_calls>
```

## Tool Discovery

The `opencode-bridge` MCP tools are registered through the OpenCode bridge system. The available tools include:

### TUI Interaction Tools

| Tool | Description |
|------|-------------|
| `opencode-bridge_tui_get_sessions` | Get a list of all sessions from the TUI API |
| `opencode-bridge_tui_get_session` | Get details about a specific session |
| `opencode-bridge_tui_get_config` | Get the TUI configuration |
| `opencode-bridge_tui_get_projects` | Get a list of all projects |
| `opencode-bridge_tui_get_current_project` | Get the current project |
| `opencode-bridge_tui_test_connection` | Test connection to the TUI API |

### File System Tools

| Tool | Description |
|------|-------------|
| `opencode-bridge_read_file` | Reads a file from the local filesystem |
| `opencode-bridge_write_file` | Writes content to a file |
| `opencode-bridge_edit_file` | Performs exact string replacements in files |
| `opencode-bridge_glob_files` | Fast file pattern matching |
| `opencode-bridge_grep_search` | Fast content search using regex |
| `opencode-bridge_list_dir` | Lists files and directories |

### Other Tools

| Tool | Description |
|------|-------------|
| `opencode-bridge_run_bash` | Executes a given bash command |
| `opencode-bridge_fetch_web` | Fetches content from a URL |
| `opencode-bridge_todowrite` | Create and manage a structured task list |
| `opencode-bridge_todoread` | Read the todo list |

## Detailed Documentation

For comprehensive documentation on all tools and their parameters, refer to the [MCP_TOOLS.md](./MCP_TOOLS.md) file.

## Making Tools Discoverable for AI Assistants

To ensure AI assistants can discover and use these tools:

1. **Configuration File**: The `opencode.json` file includes a description and list of available tools:
   ```json
   "opencode-bridge": {
     "type": "local",
     "command": ["bash", "-c", "cd /root/code/project-brainsurgeon && . venv/bin/activate && python mcp_server.py"],
     "enabled": true,
     "description": "Provides custom MCP tools for TUI interaction and enhanced file operations. Tools use prefix 'opencode-bridge_'. See MCP_TOOLS.md for complete documentation.",
     "tools": [
       "opencode-bridge_tui_get_sessions",
       "opencode-bridge_tui_get_config",
       "opencode-bridge_read_file",
       ...
     ]
   }
   ```

2. **Documentation File**: The `MCP_TOOLS.md` file provides comprehensive documentation on all tools.

3. **README Reference**: The project README.md includes examples of using the tools.

4. **Environment Information**: When starting a conversation with an AI assistant, you can include information about the available tools:
   ```
   You have access to custom MCP tools with the prefix opencode-bridge_. 
   See MCP_TOOLS.md for documentation.
   ```

## Example Usage

Here's an example of using the `opencode-bridge_tui_get_sessions` tool:

```
<function_calls>
<invoke name="opencode-bridge_tui_get_sessions">
</invoke>
</function_calls>
```

And here's an example of reading a file:

```
<function_calls>
<invoke name="opencode-bridge_read_file">
<parameter name="filePath">/path/to/file.txt</parameter>
</invoke>
</function_calls>
```