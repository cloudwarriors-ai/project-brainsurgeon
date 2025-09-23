import asyncio
import json
import os
import httpx

async def test_mcp_server():
    """Test the MCP server by connecting to it and making some requests."""
    print("Testing MCP server...")
    
    # Use subprocess to communicate with the MCP server
    async with httpx.AsyncClient(base_url="http://localhost:7777") as client:
        try:
            # Test getting sessions
            response = await client.get("/session")
            if response.status_code == 200:
                sessions = response.json()
                print(f"Successfully retrieved {len(sessions)} sessions")
                if sessions:
                    session_id = sessions[0]["id"]
                    print(f"First session ID: {session_id}")
                    
                    # Test getting session details
                    session_response = await client.get(f"/session/{session_id}")
                    if session_response.status_code == 200:
                        session_details = session_response.json()
                        print(f"Session title: {session_details.get('title', 'Unknown')}")
                    else:
                        print(f"Failed to get session details: {session_response.status_code}")
            else:
                print(f"Failed to get sessions: {response.status_code}")
            
            # Test getting configuration
            config_response = await client.get("/config")
            if config_response.status_code == 200:
                config = config_response.json()
                print(f"Successfully retrieved configuration, theme: {config.get('theme', 'Unknown')}")
            else:
                print(f"Failed to get configuration: {config_response.status_code}")
            
            # Test getting projects
            projects_response = await client.get("/project")
            if projects_response.status_code == 200:
                projects = projects_response.json()
                print(f"Successfully retrieved {len(projects)} projects")
            else:
                print(f"Failed to get projects: {projects_response.status_code}")
            
            # Test getting current project
            current_project_response = await client.get("/project/current")
            if current_project_response.status_code == 200:
                current_project = current_project_response.json()
                print(f"Current project directory: {current_project.get('worktree', 'Unknown')}")
            else:
                print(f"Failed to get current project: {current_project_response.status_code}")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())