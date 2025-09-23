#!/usr/bin/env python3

import asyncio
import httpx

# TUI API endpoint
TUI_API_URL = "http://localhost:7777"

async def call_tui_api(endpoint, method="GET", data=None):
    """Call the TUI API with the given endpoint and method."""
    url = f"{TUI_API_URL}/{endpoint}"
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

async def test_submit_prompt():
    """Test the submit prompt functionality."""
    try:
        print("Testing submit prompt...")
        result = await call_tui_api("tui/submit-prompt", method="POST", data={})
        print(f"Submit result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

async def test_append_prompt():
    """Test the append prompt functionality."""
    try:
        print("Testing append prompt...")
        data = {"text": "write a poem about chad"}
        result = await call_tui_api("tui/append-prompt", method="POST", data=data)
        print(f"Append result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

async def main():
    print("Testing TUI submit functionality...")
    
    # First append some text
    await test_append_prompt()
    
    # Wait a moment
    await asyncio.sleep(1)
    
    # Then submit it
    await test_submit_prompt()

if __name__ == "__main__":
    asyncio.run(main())