#!/usr/bin/env python3

import asyncio
import httpx

async def test_session_messages():
    """Test the new session messages endpoint directly."""
    url = "http://localhost:7777/session/ses_6890c3f31ffeMj1TowSO1g0haj/message"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Session messages retrieved successfully!")
                print(f"📊 Number of messages: {len(data)}")
                print(f"🎯 First message preview: {data[0]['info']['role'] if data else 'No messages'}")
                return True
            else:
                print(f"❌ Failed to get session messages: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_session_messages())
    exit(0 if result else 1)