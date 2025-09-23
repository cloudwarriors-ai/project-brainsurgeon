import asyncio
import httpx
import json
import sys

# TUI API endpoint
TUI_API_URL = "http://localhost:7777"

async def get_sessions():
    """Get a list of all sessions from the TUI API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TUI_API_URL}/session")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get sessions: {response.status_code}"}

async def get_session(session_id):
    """Get details about a specific session from the TUI API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TUI_API_URL}/session/{session_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get session: {response.status_code}"}

async def get_config():
    """Get the TUI configuration."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TUI_API_URL}/config")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get config: {response.status_code}"}

async def send_prompt(session_id, text, provider_id="openrouter", model_id="anthropic/claude-3.7-sonnet"):
    """Send a prompt to a session using the TUI API."""
    data = {
        "model": {
            "providerID": provider_id,
            "modelID": model_id
        },
        "parts": [
            {
                "type": "text",
                "text": text
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{TUI_API_URL}/session/{session_id}/prompt", json=data)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to send prompt: {response.status_code}, {response.text}"}
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}

async def main():
    """Main function to demonstrate TUI API integration."""
    if len(sys.argv) < 2:
        print("Usage: python connect_tui.py <command> [args...]")
        print("Commands:")
        print("  sessions - List all sessions")
        print("  session <id> - Get details about a specific session")
        print("  config - Get the TUI configuration")
        print("  prompt <session_id> <text> - Send a prompt to a session")
        return

    command = sys.argv[1]
    
    if command == "sessions":
        sessions = await get_sessions()
        print(json.dumps(sessions, indent=2))
    
    elif command == "session" and len(sys.argv) > 2:
        session_id = sys.argv[2]
        session = await get_session(session_id)
        print(json.dumps(session, indent=2))
    
    elif command == "config":
        config = await get_config()
        print(json.dumps(config, indent=2))
    
    elif command == "prompt" and len(sys.argv) > 3:
        session_id = sys.argv[2]
        text = sys.argv[3]
        result = await send_prompt(session_id, text)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())