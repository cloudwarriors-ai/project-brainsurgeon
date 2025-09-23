# Decommissioned JS MCP Server

This folder contains the decommissioned JavaScript MCP server (`mcp-tui-server.js`).

## Reason for Decommissioning
- The server failed to start due to bugs in the @modelcontextprotocol/sdk, specifically in `Server.setRequestHandler`.
- Replaced with the Python FastMCP server (`mcp_server.py`) for better reliability and tool support.

## Original Functionality
- Provided MCP tools for controlling the TUI (append prompt, submit, clear, show toast, execute command, get next event).
- Included event streaming from the opencode server at localhost:6969.

## Notes
- If the MCP SDK is fixed in future versions, this server could be revived.
- Dependencies: @modelcontextprotocol/sdk, @opencode-ai/sdk, eventsource.