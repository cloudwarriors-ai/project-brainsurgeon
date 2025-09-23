# Opencode Bridge Event Forwarder

This project provides scripts to capture events from the Opencode Bridge API and forward them to a background agent for processing. It also includes an MCP (Model Context Protocol) server with custom tools for AI assistants.

## Files

- `event-forwarder.js` - Basic implementation of an event forwarder (ES module version)
- `opencode-event-forwarder.js` - More complete implementation with event buffering and retry logic
- `opencode-api-integration.js` - Example showing how to integrate with the Opencode Bridge API
- `test-event-forwarder.js` - Test script to verify the event forwarding functionality
- `mcp_server.py` - The Opencode Bridge MCP server with event forwarding functionality
- `opencode.json` - Configuration file for Opencode with event forwarder agent defined
- `.env` - Environment variables for the bridge and event forwarder
- `start-bridge-with-agent.sh` - Script to start both the MCP server and a mock agent
- `MCP_TOOLS.md` - Comprehensive documentation for the Opencode Bridge MCP tools

## How to Use

### Prerequisites

- Node.js (v14 or later recommended)
- npm or yarn
- Access to the Opencode Bridge API

### Installation

1. Clone this repository
2. Install dependencies:

```bash
npm install axios
```

### Configuration

Set the following environment variables to configure the event forwarder:

- `AGENT_ENDPOINT` - URL of the agent API endpoint (default: `http://localhost:3000/agent`)

### Running the Event Forwarder

```bash
# Run the basic event forwarder
node event-forwarder.js

# Run the more complete event forwarder
node opencode-event-forwarder.js

# Run the Opencode Bridge with event forwarding
./start-bridge-with-agent.sh
```

### Testing

```bash
# Run the test script
node test-event-forwarder.js
```

### Opencode Integration

The project is configured to work with Opencode through the `opencode.json` configuration file:

```json
{
  "mcp": {
    "opencode-bridge": {
      "type": "local",
      "command": ["bash", "-c", "cd /root/code/project-brainsurgeon && . venv/bin/activate && python mcp_server.py"],
      "enabled": true,
      "description": "Provides custom MCP tools for TUI interaction and enhanced file operations. Tools use prefix 'opencode-bridge_'. See MCP_TOOLS.md for complete documentation."
    },
    "event-forwarder": {
      "type": "local",
      "command": ["node", "/root/code/project-brainsurgeon/opencode-event-forwarder.js"],
      "enabled": true,
      "env": {
        "AGENT_ENDPOINT": "http://localhost:3000/agent"
      }
    }
  }
}
```

This configuration:
1. Runs the Opencode Bridge MCP server
2. Runs the event-forwarder agent that listens for events and forwards them to the specified endpoint

## Integration with Opencode Bridge API

The actual integration with the Opencode Bridge API will depend on how the API is exposed. In the current implementation, we're using placeholder functions that would need to be replaced with actual API calls.

In a real implementation, you would:

1. Import or initialize the Opencode Bridge client
2. Set up event listeners or polling mechanisms
3. Forward events to your agent

See `opencode-api-integration.js` for more details on how this might be implemented.

## Opencode Bridge MCP Tools

The `opencode-bridge` MCP server provides custom tools that can be used by AI assistants to interact with the TUI and perform various operations. These tools use the prefix `opencode-bridge_`.

For comprehensive documentation, see [MCP_TOOLS.md](./MCP_TOOLS.md).

### Example Usage in AI Assistants

Here are examples of how to use the opencode-bridge tools in AI assistants:

#### Getting TUI Sessions

```javascript
// Example: Get all TUI sessions
const sessions = await opencode-bridge_tui_get_sessions();
// Returns a list of all TUI sessions
```

#### Reading and Writing Files

```javascript
// Example: Read a file
const fileContent = await opencode-bridge_read_file({
  filePath: "/path/to/file.txt"
});

// Example: Write to a file
await opencode-bridge_write_file({
  filePath: "/path/to/new-file.txt",
  content: "This is the file content"
});
```

#### Searching for Files

```javascript
// Example: Find all Python files
const pythonFiles = await opencode-bridge_glob_files({
  pattern: "**/*.py"
});

// Example: Search for text in files
const searchResults = await opencode-bridge_grep_search({
  pattern: "function getUser",
  include: "*.js"
});
```

#### Managing Todo Lists

```javascript
// Example: Create a todo list
await opencode-bridge_todowrite({
  todos: [
    {
      content: "Task 1", 
      status: "pending", 
      priority: "high", 
      id: "1"
    },
    {
      content: "Task 2", 
      status: "completed", 
      priority: "medium", 
      id: "2"
    }
  ]
});

// Example: Read the todo list
const todos = await opencode-bridge_todoread();
```

## Background Agent

The event forwarder forwards events to a background agent API. The agent can be any service that accepts HTTP POST requests with JSON payloads. The payload format is:

```json
{
  "event": {
    "type": "event.type",
    "properties": {
      "timestamp": 1758551400574,
      "data": { ... }
    }
  }
}
```

Or for batched events:

```json
{
  "events": [
    {
      "type": "event.type",
      "properties": { ... }
    },
    ...
  ]
}
```

## Development

### Adding New Features

To add new features to the event forwarder:

1. Fork this repository
2. Implement your changes
3. Add tests
4. Submit a pull request

### Architecture

The event forwarder uses a simple architecture:

1. Event Capture - Captures events from the Opencode Bridge API
2. Event Buffering - Buffers events to optimize forwarding
3. Event Forwarding - Forwards events to the background agent
4. Error Handling - Handles errors and retries failed requests

### Adding New MCP Tools

To add a new tool to the Opencode Bridge MCP server:

1. Open `mcp_server.py`
2. Add a new function with the `@app.tool()` decorator
3. Implement your tool's functionality
4. Restart the MCP server using `./start_mcp_server.sh`
5. Update `MCP_TOOLS.md` with documentation for your new tool