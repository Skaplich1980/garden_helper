# -*- coding: utf-8 -*-
import asyncio
import httpx
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test():
    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
            # Test root
            r = await client.get("/")
            print(f"Root: {r.status_code} - {r.json()['message']}")
            
            # Test reminders endpoint
            r = await client.get("/reminders/", params={"month": 9})
            print(f"Reminders: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"Found {len(data)} reminders for September")
                for item in data[:3]:
                    print(f"  - {item['crop_name']}: {item['tip_text'][:30]}...")
            else:
                print(f"Error: {r.text}")
                
            # Test users register
            r = await client.post("/users/register", json={"telegram_username": "testuser"})
            print(f"Register: {r.status_code} - {r.json().get('message', r.json())}")
            
            # Test tasks create
            r = await client.post("/tasks/", json={"telegram_username": "testuser", "title": "Test Task", "task_type": "general"})
            print(f"Create Task: {r.status_code}")
            if r.status_code == 201:
                print(f"Task created: {r.json()['id']} - {r.json()['title']}")
            else:
                print(f"Error: {r.text}")
                
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
