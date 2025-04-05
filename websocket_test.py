import asyncio
import websockets
import json

async def test_websocket():
    print("Connecting to WebSocket server...")
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            print("Connected to WebSocket server!")
            
            # Send a test message
            test_job_description = "Looking for a Python developer with 3+ years experience"
            print(f"Sending job description: {test_job_description}")
            await websocket.send(test_job_description)
            
            # Wait for response
            print("Waiting for response...")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=30)
                print("Received response:", response[:100], "..." if len(response) > 100 else "")
                print("WebSocket connection test successful!")
            except asyncio.TimeoutError:
                print("Timeout waiting for response")
    except Exception as e:
        print(f"Error connecting to WebSocket server: {e}")

async def test_http_endpoint():
    print("\nTesting HTTP endpoint...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Health check successful! Response: {data}")
                else:
                    print(f"Health check failed! Status: {response.status}")
    except Exception as e:
        print(f"Error connecting to HTTP endpoint: {e}")

if __name__ == "__main__":
    print("WebSocket Connection Test Script")
    print("===============================")
    
    # Run both tests
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_http_endpoint())
    loop.run_until_complete(test_websocket()) 