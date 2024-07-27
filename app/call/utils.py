import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def send_conversation(data):
    uri = os.getenv('WS_URL')
    identifier = data.get('sid')
    async with websockets.connect(uri) as websocket:
        await websocket.send(identifier)
        await websocket.send(json.dumps(data))
        print('hello')
        response = await websocket.recv()
        print(f"Received from ws server: {json.loads(response)}")
