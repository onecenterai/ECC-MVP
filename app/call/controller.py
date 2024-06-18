from flask import Blueprint, request
#from app.route_guard import platform_auth_required

from app.call.model import Call

from helpers.langchain import qa_chain

from logger import socket_logger
#from twilio.twiml.voice_response import VoiceResponse

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
    
    # res, success = query(partner.corpus_id, question)
    # if success and (not 'returned results did not contain sufficient information to be summarized into a useful answer for your query' in res.json().get('responseSet')[0].get('summary')[0].get('text')):
    #     answer = qa(question, res.json().get('responseSet')[0].get('summary')[0].get('text'))
    # else:
    #     answer = "Sorry, I don't have answer for that at the moment."

    Call.create(session_id=session_id, question=question, answer=answer)
    return answer

@bp.post('/call/status')
#@platform_auth_required
def get_call_status():
    return ""

from twilio.twiml.voice_response import VoiceResponse, Gather

@bp.post('/call/twilio/callback')
def ivr():
    try:
        response = VoiceResponse()

        gather = Gather(input='speech', action='call//handle_speech')
        gather.say('ECC, What is your Emergency?')
        response.append(gather)

        response.redirect('/call/twilio/callback')

        return str(response)
    except Exception as e:
         raise e

@bp.post("call/twilio/handle-speech")
def handle_speech():
    response = VoiceResponse()
    speech_result = request.values.get('SpeechResult').lower()
    
    print(vars(request.values))

    response.say('Nigga !!')

    return str(response)
     
