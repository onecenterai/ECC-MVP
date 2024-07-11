from flask import Blueprint, request

from app.call.model import Call
from helpers.langchain import qa_chain

from twilio.twiml.voice_response import VoiceResponse, Gather, Start, Stream

bp = Blueprint('call', __name__, template_folder='templates')


#############################################################################################################################
'''
################################################ TESTING ENDPOINTS ON POSTMAN ###############################################
'''
#############################################################################################################################

@bp.post('/call/initialize')
#@platform_auth_required
def make_intial_call_response():
        try:
            session_id = request.json.get('sessionId')
            answer = f"Hello, welcome to the Emergercy Hotline! How may I assist you today?"
            Call.create(session_id=session_id, question="Hello", answer=answer)
            return answer
        except Exception as e:
             raise e

@bp.post('/call/inprogress')
#@platform_auth_required
def respond_to_call_in_progress():
    answer = "Sorry, could you repeat that please?"  
    # do radysis logic here
    session_id = request.json.get('sessionId')
    question = request.json.get('text')
    
    history = Call.get_by_session_id(session_id)
    answer = qa_chain(question, history)
    
    Call.create(session_id=session_id, question=question, answer=answer)
    return answer



#############################################################################################################################
'''
############################### TWILIO (TRANSCRIPTION MODEL IS NOT GOOD) - FOR TESTING SOCKETS ##############################
'''
#############################################################################################################################

import asyncio
import websockets
import json

async def send_conversation(data):
    uri = 'ws://localhost:6789'
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(data))

@bp.post('/call/twilio/callback')
def ivr():
    try:
        response = VoiceResponse()

        data = request.values
        Call.create(from_phone=data.get('Caller'), session_id=data.get('CallSid'), question='Hello', answer='ECC, What is your Emergency?')

        payload = {
            'question': 'Hello',
            'answer': 'ECC, What is your Emergency?',
            'from_phone': data.get('Caller'),
            'sid': data.get('CallSid')
        }

        asyncio.run(send_conversation(payload))


        gather = Gather(input='speech', action='/call/twilio/handle-speech')    
        gather.say('ECC, What is your Emergency?')
        response.append(gather)

        response.redirect('/call/twilio/callback')

        return str(response)
    
    except Exception as e:
         raise e

@bp.post("/call/twilio/handle-speech")
def handle_speech():
    try:
        response = VoiceResponse()
        data = request.values
        question = data.get('SpeechResult').lower()
        from_phone = data.get('Caller')
        sid = data.get('CallSid')

        history = Call.get_by_session_id(sid)
        answer = qa_chain(question=question, history=history)
        Call.create(from_phone=from_phone, session_id=sid, question=question, answer=answer)

        payload = {
            'question': question,
            'answer': answer,
            'from_phone': from_phone,
            'sid': sid
        }

        asyncio.run(send_conversation(payload))
        
        gather = Gather(input='speech', action='/call/twilio/handle-speech')    
        gather.say(answer)
        response.append(gather)

        #response.redirect('/call/twilio/callback')

        response.say('Nigga !!')
        return str(response)
        
    except Exception as e:
        # If error occur forward the call
        print(e)
        response.say('Nigga !!')
        return str(response)


#############################################################################################################################
'''
####################################### THIS SECTION IS FOR STREAMING - STILL UNDER PROGRESS ################################
'''
#############################################################################################################################

from app import sock
import audioop, json, base64, wave, time, os
from dotenv import load_dotenv

load_dotenv()

SILENCE_THRESHOLD = os.getenv('SILENCE_THRESHOLD')
SILENCE_DURATION = os.getenv('SILENCE_DURATION')


# @bp.post('/call/twilio/callback')
# def ivr():
#     try:
#         response = VoiceResponse()

#         data = request.values
#         Call.create(from_phone=data.get('Caller'), session_id=data.get('CallSid'), question='Hello', answer='ECC, What is your Emergency?')

#         start = Start()
#         start.stream(url=f'wss://{request.host}/stream')
#         response.append(start)
#         response.say('ECC What is your emergency')
#         response.pause(length=10)


#         return str(response), 200, {'Content-Type': 'text/xml'}
    
#     except Exception as e:
#          raise e

def save_audio_wf(audio_data, filename="./output-wf.wav"):

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(16000)  # 16kHz sample rate
        wf.writeframes(audio_data)

@sock.route('/stream')
def stream(ws):
    try:
        audio_buffer = b''
        
        while True:
            message = ws.receive()
            packet = json.loads(message)
            if packet['event'] == 'start':
                print('Starting Stream')
            elif packet['event'] == 'stop':
                print('Stopping Stream')
                save_audio_wf(audio_buffer)
                audio_buffer = b''
            elif packet['event'] == 'media':
                audio = base64.b64decode(packet['media']['payload'])
                audio = audioop.ulaw2lin(audio, 2)
                audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]
                audio_buffer += audio
                
                '''
                    NOTE !!
                    DETECT SILENCE AND SEND MESSAGE TO LLM MODEL
                    STILL UNDER WORK SHA
                '''
                # # Append to the main audio buffer
                # audio_buffer += audio
                
                # # Check for silence
                # rms = audioop.rms(audio, 2)
                # if rms < SILENCE_THRESHOLD:
                #     if silence_start is None:
                #         silence_start = time.time()
                #     silence_buffer += audio
                # else:
                #     silence_start = None
                #     silence_buffer = b''
                
                # if silence_start and (time.time() - silence_start) >= SILENCE_DURATION:
                #     print('Silence Detected, stopping stream.')
                #     save_audio_wf(audio_buffer)
                #     audio_buffer = b''
                #     break  # Exit the loop if silence is detected for a duration # Append to the main audio buffer
                # audio_buffer += audio
                
                # # Check for silence
                # rms = audioop.rms(audio, 2)
                # if rms < SILENCE_THRESHOLD:
                #     if silence_start is None:
                #         silence_start = time.time()
                #     silence_buffer += audio
                # else:
                #     silence_start = None
                #     silence_buffer = b''
                
                # if silence_start and (time.time() - silence_start) >= SILENCE_DURATION:
                #     print('Silence Detected, stopping stream.')
                #     save_audio_wf(audio_buffer)
                #     audio_buffer = b''
                #     break  # Exit the loop if silence is detected for a duration

    except Exception as e:
        raise e