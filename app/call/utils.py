import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
import wave
import requests

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

def send_conversation_webhook(data):
    url = os.getenv('WH_URL')
    res = requests.post(url=url, json=data)
    return res.json()

def save_audio_wf(audio_data, filename="./output-wf.wav"):

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(16000)  # 16kHz sample rate
        wf.writeframes(audio_data)
