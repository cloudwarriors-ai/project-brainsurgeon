# OpenCode Event Monitoring & Supervisor Architecture

## Overview

This document outlines our investigation into the OpenCode event system and how to properly implement supervisor agents that monitor build events without getting stuck in evaluation loops.

## Initial Problem

When attempting to use a supervisor agent to monitor build events (hello-world creation, Playwright testing), the supervisor reported that no events were found, despite successful completion of all build tasks.

## Investigation Findings

### OpenCode-Bridge Tools

The available opencode-bridge MCP tools are:
- `opencode-bridge_get_next_event` ✅ **WORKS**
- `opencode-bridge_append_prompt` ❌ **FAILS** (Extra data error)
- `opencode-bridge_submit_prompt` ❌ **FAILS** (Extra data error) 
- `opencode-bridge_clear_prompt` ❌ **FAILS** (Extra data error)
- `opencode-bridge_show_toast` ❌ **FAILS** (Extra data error)
- `opencode-bridge_execute_command` ❌ **FAILS** (Extra data error)

**Error Pattern**: All action functions fail with `"Extra data: line 1 column 5 (char 4)"` suggesting JSON parsing/protocol issues.

### Event System Architecture

Based on [OpenCode Server Documentation](https://opencode.ai/docs/server/):

1. **Events API**: `GET /event` provides server-sent events stream
2. **Event Flow**: `server.connected` event first, then bus events
3. **Session-based**: Each session has unique ID with parent-child relationships
4. **TUI Integration**: Events are generated from TUI interactions, not tool executions

### Key Discovery: Event Source Mismatch

**What We Expected**: Tool executions (file writes, bash commands, test runs) would generate events

**Reality**: OpenCode events come from **UI/TUI interactions** (user inputs, command submissions, interface actions), not from **tool execution activities**

This explains why our build activities (creating files, running Playwright tests) didn't generate events in the OpenCode event stream.

## The Evaluation Loop Problem

### Issue Identified
- Supervisor calls `get_next_event` → potentially generates events
- Supervisor monitors its own event generation → infinite loop
- Need to differentiate between supervisor events and build agent events

### Root Cause
Supervisor agents monitoring the same event stream they're generating events on.

## Solution: Agent Differentiation via Instructions

### Approach: Smart Instructions (Not MCP Modification)

**Recommendation**: Use intelligent prompting rather than modifying MCP tools.

### Supervisor Instructions Template

```
You are the supervisor agent. When monitoring events:

1. **Parse Event Structure**: Extract session ID, agent ID, or source identifier from each event
2. **Filter Self-Events**: If event.sessionID == your_own_session_id, skip processing
3. **Target Filtering**: Only process events from the main build agent's session
4. **Event Types**: Focus on build-related events (file operations, test executions, etc.)
5. **Reporting**: Report only on events that match the target build activities

Avoid monitoring your own supervision activities to prevent evaluation loops.
```

### Implementation Strategy

1. **Session Isolation**: Run supervisor in separate session/context from build agent
2. **Event Parsing**: When events contain session/agent metadata, use it for filtering
3. **Smart Filtering**: Only report events from non-supervisor sessions
4. **Targeted Monitoring**: Focus on specific event types related to build activities

## Event Generation Testing Results

### File Operations Test
- Created `test-event-generation.txt` via write tool
- Created `bash-test.txt` via bash command
- **Result**: No events generated in OpenCode event stream

### Conclusion
Tool executions don't generate OpenCode bus events. Events likely come from:
- User interface interactions
- TUI command submissions
- Session management operations
- Agent-to-agent communications

## Current Status

### What Works
- ✅ Event monitoring via `get_next_event`
- ✅ Build activities (file creation, testing) complete successfully
- ✅ Understanding of event system architecture

### What Needs Implementation
- 🔄 Event filtering logic in supervisor instructions
- 🔄 Session-aware event processing
- 🔄 Testing with actual event generation scenarios

## Recommendations

### For Build Monitoring
1. **Alternative Approach**: Monitor file system changes directly rather than relying on OpenCode events
2. **Hybrid Monitoring**: Use event stream for UI events + file watching for build events
3. **Session Management**: Properly isolate supervisor and build agent sessions

### For Event System Usage
1. **Focus on UI Events**: Use event monitoring for user interaction tracking
2. **Tool Results**: Monitor build success through direct tool outputs rather than events
3. **Agent Coordination**: Use events for inter-agent communication, not build monitoring

## Technical Notes

### Event Stream Behavior
- Consistently returns `{"error":"No event available"}` when no events are queued
- Event monitoring function is responsive and working correctly
- No evidence of event generation from standard development tool usage

### Bridge Tool Issues
- Action functions have protocol/parsing errors
- Only read-only `get_next_event` functions properly
- May indicate version mismatch or configuration issue

## Next Steps

1. **Test Event Generation**: Find activities that DO generate OpenCode events
2. **Implement Filtering**: Add session-aware filtering to supervisor instructions
3. **Alternative Monitoring**: Develop file-system based build monitoring
4. **Debug Bridge Tools**: Investigate why action functions fail with parsing errors

---

**Last Updated**: Sep 22, 2025  
**Status**: Investigation Complete, Implementation Pending