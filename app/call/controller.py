from flask import Blueprint, request

from app.call.model import Call

from helpers.langchain import qa_chain

from twilio.twiml.voice_response import VoiceResponse, Gather, Start, Stream


bp = Blueprint('call', __name__, template_folder='templates')

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




# @bp.post('/call/twilio/callback')
# def ivr():
#     try:
#         response = VoiceResponse()

#         data = request.values
#         Call.create(from_phone=data.get('Caller'), session_id=data.get('CallSid'), question='Hello', answer='ECC, What is your Emergency?')

#         gather = Gather(input='speech', action='/call/twilio/handle-speech')    
#         gather.say('ECC, What is your Emergency?')
#         response.append(gather)

#         response.redirect('/call/twilio/callback')

#         return str(response)
    
#     except Exception as e:
#          raise e

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
     

from app import sock
import audioop, json, base64, wave


@bp.post('/call/twilio/callback')
def ivr():
    try:
        response = VoiceResponse()

        data = request.values
        Call.create(from_phone=data.get('Caller'), session_id=data.get('CallSid'), question='Hello', answer='ECC, What is your Emergency?')

        start = Start()
        start.stream(url=f'wss://{request.host}/stream')
        response.append(start)
        response.say('ECC What is your emergency')
        response.pause(length=10)


        return str(response), 200, {'Content-Type': 'text/xml'}
    
    except Exception as e:
         raise e

def save_audio_to_file(audio_data, filename="/audio-files/output.wav"):

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
                save_audio_to_file(audio_buffer)
                audio_buffer = b''
            elif packet['event'] == 'media':
                audio = base64.b64decode(packet['media']['payload'])
                audio = audioop.ulaw2lin(audio, 2)
                audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]
                audio_buffer += audio
    except Exception as e:
        raise e