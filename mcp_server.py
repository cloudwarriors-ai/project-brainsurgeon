import asyncio
import json
import os
import subprocess
import glob as glob_module
import re
import httpx
import inspect
from typing import Optional, Dict, Any, List, Set
import tempfile

from fastmcp import FastMCP

# Create the MCP app
app = FastMCP("opencode")

# Working directory
WORKING_DIR = "/root/code/project-brainsurgeon"

# TUI API endpoint (default)
TUI_API_URL = "http://localhost:7777"

# Global todo list
todo_list = []

# Track registered tools
tool_registry = {}

# Connection registry for multiple TUI instances
connection_registry = {}
active_connection_id = None

# Helper function to get connection URL
def get_connection_url(connection_id=None):
    """Get the URL for a specific connection or the default/active one."""
    if connection_id:
        if connection_id in connection_registry:
            return connection_registry[connection_id]["url"]
        else:
            raise ValueError(f"Connection '{connection_id}' not found")
    elif active_connection_id and active_connection_id in connection_registry:
        return connection_registry[active_connection_id]["url"]
    else:
        return TUI_API_URL

# Helper function to call TUI API
async def call_tui_api(endpoint, method="GET", data=None, connection_id=None):
    """Call the TUI API with the given endpoint and method."""
    base_url = get_connection_url(connection_id)
    url = f"{base_url}/{endpoint}"
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=data)
        elif method == "PUT":
            response = await client.put(url, json=data)
        elif method == "DELETE":
            response = await client.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code >= 400:
            return {"error": f"API request failed with status code {response.status_code}"}
        
        return response.json()

@app.tool()
async def run_bash(command: str, timeout: int = 120000, description: str = ""):
    """Executes a given bash command with optional timeout."""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=WORKING_DIR
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout/1000.0)
        return {
            "stdout": stdout.decode('utf-8', errors='replace'),
            "stderr": stderr.decode('utf-8', errors='replace'),
            "returncode": process.returncode
        }
    except asyncio.TimeoutError:
        process.kill()
        return {"error": "Command timed out"}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def edit_file(filePath: str, oldString: str, newString: str, replaceAll: bool = False):
    """Performs exact string replacements in files."""
    try:
        with open(filePath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if replaceAll:
            new_content = content.replace(oldString, newString)
        else:
            if oldString not in content:
                return {"error": "oldString not found in content"}
            new_content = content.replace(oldString, newString, 1)
        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def fetch_web(url: str, format: str = "text", timeout: int = 120):
    """Fetches content from a specified URL."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text
            if format == "markdown":
                # Simple markdown conversion (basic)
                content = content.replace('<', '&lt;').replace('>', '&gt;')
            return {"content": content}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def glob_files(pattern: str, path: str = None):
    """Fast file pattern matching."""
    try:
        search_path = path or WORKING_DIR
        matches = glob_module.glob(os.path.join(search_path, pattern), recursive=True)
        return {"matches": matches}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def grep_search(pattern: str, path: str = None, include: str = None):
    """Fast content search using regex."""
    try:
        search_path = path or WORKING_DIR
        matches = []
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if include and not glob_module.fnmatch(file, include):
                    continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if re.search(pattern, line):
                                matches.append({
                                    "path": filepath,
                                    "line": line_num,
                                    "content": line.strip()
                                })
                except:
                    pass
        return {"matches": matches[:100]}  # Limit results
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def list_dir(path: str, ignore: List[str] = None):
    """Lists files and directories in a given path."""
    try:
        entries = os.listdir(path)
        if ignore:
            filtered = []
            for entry in entries:
                skip = False
                for pattern in ignore:
                    if glob_module.fnmatch(entry, pattern):
                        skip = True
                        break
                if not skip:
                    filtered.append(entry)
            entries = filtered
        return {"entries": entries}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def read_file(filePath: str, offset: int = 0, limit: int = 2000):
    """Reads a file from the local filesystem."""
    try:
        with open(filePath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        start = offset
        end = min(start + limit, len(lines))
        content = ''.join(lines[start:end])
        return {"content": content, "lines_read": len(lines[start:end])}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def write_file(filePath: str, content: str):
    """Writes content to a file."""
    try:
        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def todowrite(todos: List[Dict[str, Any]]):
    """Create and manage a structured task list."""
    global todo_list
    todo_list = todos
    return {"success": True}

@app.tool()
async def todoread():
    """Read the todo list."""
    return {"todos": todo_list}

# Connection management tools
@app.tool()
async def add_connection(connection_id: str, url: str, project_name: str = None, description: str = None):
    """Add a new TUI connection to the registry."""
    global connection_registry
    
    # Test the connection first
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            test_endpoints = ["/doc", "/", "/status", "/health", "/app"]
            connection_valid = False
            
            for endpoint in test_endpoints:
                try:
                    response = await client.get(f"{url}{endpoint}")
                    if response.status_code in [200, 404]:
                        connection_valid = True
                        break
                except:
                    continue
            
            if not connection_valid:
                return {"error": f"Unable to connect to TUI at {url}"}
                
    except Exception as e:
        return {"error": f"Connection test failed: {str(e)}"}
    
    # Get project info if possible
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{url}/project/current")
            if response.status_code == 200:
                project_info = response.json()
                if not project_name and project_info.get("worktree"):
                    project_name = os.path.basename(project_info["worktree"])
    except:
        pass
    
    connection_registry[connection_id] = {
        "url": url,
        "project_name": project_name,
        "description": description,
        "added_at": asyncio.get_event_loop().time()
    }
    
    return {
        "success": True,
        "connection_id": connection_id,
        "url": url,
        "project_name": project_name
    }

@app.tool()
async def remove_connection(connection_id: str):
    """Remove a TUI connection from the registry."""
    global connection_registry, active_connection_id
    
    if connection_id not in connection_registry:
        return {"error": f"Connection '{connection_id}' not found"}
    
    del connection_registry[connection_id]
    
    # Clear active connection if it was the one being removed
    if active_connection_id == connection_id:
        active_connection_id = None
    
    return {"success": True, "removed": connection_id}

@app.tool()
async def list_connections():
    """List all registered TUI connections."""
    connections = []
    for conn_id, conn_info in connection_registry.items():
        connections.append({
            "connection_id": conn_id,
            "url": conn_info["url"],
            "project_name": conn_info.get("project_name"),
            "description": conn_info.get("description"),
            "is_active": conn_id == active_connection_id
        })
    
    return {
        "connections": connections,
        "active_connection": active_connection_id,
        "default_url": TUI_API_URL
    }

@app.tool()
async def set_active_connection(connection_id: str = None):
    """Set the active TUI connection. Use None to clear active connection and use default."""
    global active_connection_id
    
    if connection_id is None:
        active_connection_id = None
        return {"success": True, "active_connection": None, "message": "Using default connection"}
    
    if connection_id not in connection_registry:
        return {"error": f"Connection '{connection_id}' not found"}
    
    active_connection_id = connection_id
    return {
        "success": True,
        "active_connection": connection_id,
        "url": connection_registry[connection_id]["url"]
    }

@app.tool()
async def get_connection_info(connection_id: str):
    """Get detailed information about a specific connection."""
    if connection_id not in connection_registry:
        return {"error": f"Connection '{connection_id}' not found"}
    
    conn_info = connection_registry[connection_id].copy()
    conn_info["connection_id"] = connection_id
    conn_info["is_active"] = connection_id == active_connection_id
    
    # Test current connection status
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{conn_info['url']}/doc")
            conn_info["status"] = "online" if response.status_code in [200, 404] else "offline"
    except:
        conn_info["status"] = "offline"
    
    return conn_info

# TUI-specific tools
@app.tool()
async def tui_get_sessions(connection_id: str = None):
    """Get a list of all sessions from the TUI API."""
    try:
        url = get_connection_url(connection_id)
        cmd = f"{WORKING_DIR}/tui_connector.py sessions --url {url}"
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=WORKING_DIR
        )
        stdout, stderr = await process.communicate()
        if stdout:
            return json.loads(stdout.decode('utf-8'))
        else:
            return {"error": stderr.decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def tui_get_session(session_id: str, connection_id: str = None):
    """Get details about a specific session from the TUI API."""
    try:
        url = get_connection_url(connection_id)
        cmd = f"{WORKING_DIR}/tui_connector.py session --id {session_id} --url {url}"
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=WORKING_DIR
        )
        stdout, stderr = await process.communicate()
        if stdout:
            return json.loads(stdout.decode('utf-8'))
        else:
            return {"error": stderr.decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def tui_get_config(connection_id: str = None):
    """Get the TUI configuration."""
    try:
        url = get_connection_url(connection_id)
        cmd = f"{WORKING_DIR}/tui_connector.py config --url {url}"
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=WORKING_DIR
        )
        stdout, stderr = await process.communicate()
        if stdout:
            return json.loads(stdout.decode('utf-8'))
        else:
            return {"error": stderr.decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def tui_get_projects(connection_id: str = None):
    """Get a list of all projects from the TUI API."""
    try:
        url = get_connection_url(connection_id)
        cmd = f"{WORKING_DIR}/tui_connector.py projects --url {url}"
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=WORKING_DIR
        )
        stdout, stderr = await process.communicate()
        if stdout:
            return json.loads(stdout.decode('utf-8'))
        else:
            return {"error": stderr.decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def tui_get_current_project(connection_id: str = None):
    """Get the current project from the TUI API."""
    try:
        url = get_connection_url(connection_id)
        cmd = f"{WORKING_DIR}/tui_connector.py current_project --url {url}"
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=WORKING_DIR
        )
        stdout, stderr = await process.communicate()
        if stdout:
            return json.loads(stdout.decode('utf-8'))
        else:
            return {"error": stderr.decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def tui_test_connection(url: str = TUI_API_URL, timeout: int = 5):
    """Test connection to the TUI API."""
    try:
        cmd = f"{WORKING_DIR}/tui_connector.py test_connection"
        if url != TUI_API_URL:
            cmd += f" --url {url}"
        if timeout != 5:
            cmd += f" --timeout {timeout}"
            
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=WORKING_DIR
        )
        stdout, stderr = await process.communicate()
        if stdout:
            return json.loads(stdout.decode('utf-8'))
        else:
            return {"error": stderr.decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def show_toast(message: str, variant: str = "info", title: str = None, connection_id: str = None):
    """Show a toast notification in the TUI."""
    try:
        data = {"message": message, "variant": variant}
        if title:
            data["title"] = title
        
        result = await call_tui_api("tui/show-toast", method="POST", data=data, connection_id=connection_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def tui_append_prompt(text: str, connection_id: str = None):
    """Append prompt to the TUI."""
    try:
        data = {"text": text}
        result = await call_tui_api("tui/append-prompt", method="POST", data=data, connection_id=connection_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def tui_submit_prompt(connection_id: str = None):
    """Submit the current prompt in the TUI."""
    try:
        result = await call_tui_api("tui/submit-prompt", method="POST", data={}, connection_id=connection_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.tool()
async def tui_get_session_messages(session_id: str, connection_id: str = None):
    """Get all messages for a specific session from the TUI API."""
    try:
        result = await call_tui_api(f"session/{session_id}/message", method="GET", connection_id=connection_id)
        return result
    except Exception as e:
        return {"error": str(e)}

# Tool discovery endpoint
@app.tool()
async def get_available_tools():
    """Get a list of all available tools in the opencode-bridge MCP server."""
    tools = [
        {"name": "opencode-bridge_run_bash", "description": "Executes a given bash command with optional timeout."},
        {"name": "opencode-bridge_edit_file", "description": "Performs exact string replacements in files."},
        {"name": "opencode-bridge_fetch_web", "description": "Fetches content from a specified URL."},
        {"name": "opencode-bridge_glob_files", "description": "Fast file pattern matching."},
        {"name": "opencode-bridge_grep_search", "description": "Fast content search using regex."},
        {"name": "opencode-bridge_list_dir", "description": "Lists files and directories in a given path."},
        {"name": "opencode-bridge_read_file", "description": "Reads a file from the local filesystem."},
        {"name": "opencode-bridge_write_file", "description": "Writes content to a file."},
        {"name": "opencode-bridge_todowrite", "description": "Create and manage a structured task list."},
        {"name": "opencode-bridge_todoread", "description": "Read the todo list."},
        {"name": "opencode-bridge_add_connection", "description": "Add a new TUI connection to the registry."},
        {"name": "opencode-bridge_remove_connection", "description": "Remove a TUI connection from the registry."},
        {"name": "opencode-bridge_list_connections", "description": "List all registered TUI connections."},
        {"name": "opencode-bridge_set_active_connection", "description": "Set the active TUI connection."},
        {"name": "opencode-bridge_get_connection_info", "description": "Get detailed information about a specific connection."},
        {"name": "opencode-bridge_tui_get_sessions", "description": "Get a list of all sessions from the TUI API."},
        {"name": "opencode-bridge_tui_get_session", "description": "Get details about a specific session from the TUI API."},
        {"name": "opencode-bridge_tui_get_config", "description": "Get the TUI configuration."},
        {"name": "opencode-bridge_tui_get_projects", "description": "Get a list of all projects from the TUI API."},
        {"name": "opencode-bridge_tui_get_current_project", "description": "Get the current project from the TUI API."},
        {"name": "opencode-bridge_tui_test_connection", "description": "Test connection to the TUI API."},
        {"name": "opencode-bridge_show_toast", "description": "Show a toast notification in the TUI."},
        {"name": "opencode-bridge_tui_append_prompt", "description": "Append prompt to the TUI."},
        {"name": "opencode-bridge_tui_submit_prompt", "description": "Submit the current prompt in the TUI."},
        {"name": "opencode-bridge_tui_get_session_messages", "description": "Get all messages for a specific session from the TUI API."},
        {"name": "opencode-bridge_get_available_tools", "description": "Get a list of all available tools in the opencode-bridge MCP server."}
    ]
    return {"tools": tools}

if __name__ == "__main__":
    print("Starting Opencode MCP server...")
    print("See MCP_TOOLS.md for complete documentation on available tools")
    
    # Start the MCP server
    app.run()