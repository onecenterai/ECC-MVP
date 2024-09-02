from flask import Blueprint, request, Response

from app.call.model import Call
from helpers.langchain import qa_chain
from helpers.sentiment_analyser import severity_inference_pipeline

from twilio.twiml.voice_response import VoiceResponse, Gather, Start, Stream

import asyncio, threading
from .utils import send_conversation, save_audio_wf, send_conversation_webhook

from app import sock
import audioop, json, base64, time, os
from dotenv import load_dotenv
import whisper
import numpy as np
import torch

from logger import main_logger

load_dotenv()

bp = Blueprint('call', __name__, template_folder='templates')

#whisper_model = whisper.load_model('base')
SILENCE_THRESHOLD = os.getenv('SILENCE_THRESHOLD')
SILENCE_DURATION = os.getenv('SILENCE_DURATION')

CL = '\x1b[0K'
BS = '\x08'


#############################################################################################################################
'''
################################################ TESTING ENDPOINTS ON POSTMAN ###############################################
'''
#############################################################################################################################

@bp.post('/call/initialize')
#@platform_auth_required
def make_intial_call_response():
    session_id = request.json.get('sessionId')
    answer = f"Hello, welcome to the Emergercy Hotline! How may I assist you today?"
    Call.create(session_id=session_id, question="Hello", answer=answer)

    payload = {
        'question': 'Hello',
        'answer': 'ECC, What is your Emergency?',
        'from_phone': '+2349067887538',
        'sid': session_id,
        'severity_level': 1
    }

    ws_res = send_conversation_webhook(payload)
    res = {
        'payload':payload,
        'ws_res':ws_res
    }
    
    return res


@bp.post('/call/inprogress')
def respond_to_call_in_progress():
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    session_id = request.json.get('sessionId')
    question = request.json.get('text')
    
    history = Call.get_by_session_id(session_id)
    
    results = loop.run_until_complete(asyncio.gather(
      qa_chain(question, history),
      severity_inference_pipeline(question)
    ))

    answer, severity_level = results
    
    Call.create(session_id=session_id, question=question, answer=answer)

    payload = {
                'question': question,
                'answer': answer,
                'from_phone': '+2349067887538',
                'sid': session_id,
                'severity_level': severity_level
            }

    ws_res = send_conversation_webhook(payload)
    res = {
        'payload':payload,
        'ws_res':ws_res
    }
    
    return res



#############################################################################################################################
'''
############################### TWILIO (TRANSCRIPTION MODEL IS NOT GOOD) - FOR TESTING SOCKETS ##############################
'''
#############################################################################################################################

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
            'sid': data.get('CallSid'),
            'severity_level': 1
        }

        ws_res = send_conversation_webhook(payload)
        res = {
            'payload':payload,
            'ws_res':ws_res
        }

        main_logger.info(str(res))

        gather = Gather(input='speech', 
                        action='/call/twilio/handle-speech', 
                        enhanced=True, 
                        speech_model="phone_call", )
                        # speech_timeout=2,
                        # timeout=2)
        gather.say('ECC, What is your Emergency?')
        response.append(gather)
        
        response.redirect('/call/twilio/handle-speech')

        return str(response)
    
    except Exception as e:
        main_logger.error(str(e))
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
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(asyncio.gather(
            qa_chain(question, history),
            severity_inference_pipeline(question)
        ))

        answer, severity_level = results
        
        Call.create(session_id=sid, question=question, answer=answer)

        payload = {
                    'question': question,
                    'answer': answer,
                    'from_phone': from_phone,
                    'sid': sid,
                    'severity_level': severity_level
                }
        
        ws_res = send_conversation_webhook(payload)
        res = {
            'payload':payload,
            'ws_res':ws_res
        }

        main_logger.info(str(res))

        if 'forward_call' in answer or 'human' in answer or 'agent' in answer:
            response.say('Okay, I will forward your call to a human agent, please wait')
            response.dial(os.getenv('FORWARD_CALL_NUMBER'))
            return Response(str(response), 200, mimetype="application/xml")
        else:
            gather = Gather(input='speech', 
                            action='/call/twilio/handle-speech', 
                            enhanced=True, 
                            speech_model="phone_call", )
                            # speech_timeout=2,
                            # timeout=2)
            gather.say(answer)
            response.append(gather)

            response.redirect('/call/twilio/handle-speech')

            response.say('Call Ended')
            return str(response)
        
    except Exception as e:
        # TODO: If error occur forward the call
        main_logger.error(str(e))
        response.say('An error occured')
        return str(response)


#############################################################################################################################
'''
####################################### THIS SECTION IS FOR STREAMING - STILL UNDER PROGRESS ################################
'''
#############################################################################################################################

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

# @sock.route('/stream')
# def stream(ws):
#     global i
#     global transcription0
#     try:
#         audio_buffer = b''
        
#         while True:
#             message = ws.receive()
#             packet = json.loads(message)
#             if packet['event'] == 'start':
#                 print('Starting Stream')
#             elif packet['event'] == 'stop':
#                 print('Stopping Stream')
#                 save_audio_wf(audio_buffer)
                
#                 # Convert in-ram buffer to something the model can use directly without needing a temp file.
#                 # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
#                 # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
#                 audio_np = np.frombuffer(audio_buffer, dtype=np.int64).astype(np.float32) / 32768.0

#                 transcription = whisper_model.transcribe(audio_np, fp16=torch.cuda.is_available())
#                 question = transcription['text'].strip()
#                 print(f'\nWHISPER TRANSCRIPTION: {question}\n')
#                 audio_buffer = b''
#             elif packet['event'] == 'media':
#                 i += 1
#                 audio = base64.b64decode(packet['media']['payload'])
#                 audio = audioop.ulaw2lin(audio, 2)
#                 audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]
#                 audio_buffer += audio

#                 if len(audio_buffer) > 299999:
#                     audio_file = 'transcription'+str(i)+'.wav'
#                     save_audio_wf(audio_data=audio_buffer, filename=audio_file)
#                     audio_file = open(audio_file, 'rb')


#                 # Convert in-ram buffer to something the model can use directly without needing a temp file.
#                 # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
#                 # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
#                 # audio_np = np.frombuffer(audio_buffer, dtype=np.int64).astype(np.float32) / 32768.0
#                 try:
#                     transcription = whisper_model.transcribe(audio_file)
#                     if (transcription != transcription0):
#                         print(transcription['text'] + ' ')
#                         transcription0 = transcription
#                     audio_file.close()
#                 except:
#                     print('An error occured while transcribing')
#                     pass

                
#                 audio_buffer = b''
                
#                 '''
#                     NOTE !!
#                     DETECT SILENCE AND SEND MESSAGE TO LLM MODEL
#                     STILL UNDER WORK SHA
#                 '''
#                 # # Append to the main audio buffer
#                 # audio_buffer += audio
                
#                 # # Check for silence
#                 # rms = audioop.rms(audio, 2)
#                 # if rms < SILENCE_THRESHOLD:
#                 #     if silence_start is None:
#                 #         silence_start = time.time()
#                 #     silence_buffer += audio
#                 # else:
#                 #     silence_start = None
#                 #     silence_buffer = b''
                
#                 # if silence_start and (time.time() - silence_start) >= SILENCE_DURATION:
#                 #     print('Silence Detected, stopping stream.')
#                 #     save_audio_wf(audio_buffer)
#                 #     audio_buffer = b''
#                 #     break  # Exit the loop if silence is detected for a duration # Append to the main audio buffer
#                 # audio_buffer += audio
                
#                 # # Check for silence
#                 # rms = audioop.rms(audio, 2)
#                 # if rms < SILENCE_THRESHOLD:
#                 #     if silence_start is None:
#                 #         silence_start = time.time()
#                 #     silence_buffer += audio
#                 # else:
#                 #     silence_start = None
#                 #     silence_buffer = b''

#                 # if silence_start and (time.time() - silence_start) >= SILENCE_DURATION:
#                 #     print('Silence Detected, stopping stream.')
#                 #     save_audio_wf(audio_buffer)
#                 #     audio_buffer = b''
#                 #     break  # Exit the loop if silence is detected for a duration

#     except Exception as e:
#         raise e