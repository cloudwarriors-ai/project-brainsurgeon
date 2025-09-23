#!/usr/bin/env python3
"""
TUI Connector - A bridge script for the opencode-bridge MCP server to interact with the TUI API.

This script provides functionality to connect to the opencode TUI API running on port 7777
and exposes functions that can be used by the MCP server to interact with the TUI.
"""

import asyncio
import httpx
import json
import sys
import os
import argparse

# TUI API endpoint
TUI_API_URL = "http://localhost:7777"

async def get_sessions(url=TUI_API_URL):
    """Get a list of all sessions from the TUI API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/session")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get sessions: {response.status_code}"}

async def get_session(session_id, url=TUI_API_URL):
    """Get details about a specific session from the TUI API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/session/{session_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get session: {response.status_code}"}

async def get_config(url=TUI_API_URL):
    """Get the TUI configuration."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/config")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get config: {response.status_code}"}

async def get_projects(url=TUI_API_URL):
    """Get a list of all projects from the TUI API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/project")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get projects: {response.status_code}"}

async def get_current_project(url=TUI_API_URL):
    """Get the current project from the TUI API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/project/current")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get current project: {response.status_code}"}

async def test_connection(url=TUI_API_URL, timeout=5):
    """Test connection to the TUI API."""
    try:
        # Prioritize the /doc endpoint
        doc_endpoint = "/doc"
        other_endpoints = ["/", "/status", "/health", "/app"]
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            # First try the /doc endpoint
            try:
                full_url = f"{url}{doc_endpoint}"
                response = await client.get(full_url)
                if response.status_code in [200, 404]:  # Server is responding
                    return {
                        "success": True,
                        "url": url,
                        "endpoint_tested": doc_endpoint,
                        "status_code": response.status_code,
                        "message": "Connection successful"
                    }
            except Exception as e:
                pass
                
            # Then try other endpoints as fallback
            for endpoint in other_endpoints:
                try:
                    full_url = f"{url}{endpoint}"
                    response = await client.get(full_url)
                    if response.status_code in [200, 404]:  # Server is responding
                        return {
                            "success": True,
                            "url": url,
                            "endpoint_tested": endpoint,
                            "status_code": response.status_code,
                            "message": "Connection successful"
                        }
                except Exception as e:
                    continue
                    
        # If we got here, none of the endpoints worked
        return {
            "success": False,
            "url": url,
            "error": "Server not responding to any test endpoints"
        }
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": str(e)
        }

async def main():
    """Main function to parse command line arguments and call the appropriate function."""
    parser = argparse.ArgumentParser(description="TUI Connector for MCP server")
    parser.add_argument("command", choices=["sessions", "session", "config", "projects", "current_project", "test_connection"], 
                        help="Command to execute")
    parser.add_argument("--id", help="Session ID for the session command")
    parser.add_argument("--url", help="URL for the test_connection command")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds for the test_connection command")
    args = parser.parse_args()
    
    url = args.url if args.url else TUI_API_URL
    
    if args.command == "sessions":
        result = await get_sessions(url)
    elif args.command == "session":
        if not args.id:
            print(json.dumps({"error": "Session ID is required for the session command"}))
            return
        result = await get_session(args.id, url)
    elif args.command == "config":
        result = await get_config(url)
    elif args.command == "projects":
        result = await get_projects(url)
    elif args.command == "current_project":
        result = await get_current_project(url)
    elif args.command == "test_connection":
        result = await test_connection(url, args.timeout)
    else:
        result = {"error": f"Unknown command: {args.command}"}
    
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(main())