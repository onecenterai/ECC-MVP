import asyncio
from signalwire.relay.consumer import Consumer
import os
from app.call.model import Call
from helpers.langchain import qa_chain
from app import app
from logger import sw_logger
import traceback

import whisper
model = whisper.load_model("base")

class CustomConsumer(Consumer):
    def setup(self):
        self.project = os.getenv('SW_PROJECT_ID')
        self.token = os.getenv("SW_TOKEN")
        self.contexts = ['ecc-mvp']
    
    async def on_incoming_call(self, call, question="Hello", result=None):
        try:
            with app.app_context():
                if not result:
                    sw_logger.info('\n\n--- New Call ---')
                    result = await call.answer()
                    if result.successful:
                        call_id = result.event.payload.get('call_id')
                        from_phone = result.event.payload.get('device').get('params').get('from_number')
                                                    
                        answer = f'ECC, What is your Emergency?'
                        Call.create(from_phone=from_phone, session_id=call_id, question=question, answer=answer)

                        sw_logger.info(f'\nfrom phone: {from_phone} \nquestion: {question} \nanswer: {answer}\n')

                        question_audio = await call.prompt_tts(prompt_type='speech', text=answer, speech_language='en-US')
                        audio_file_path = "./question.wav"
                        with open(audio_file_path, "wb") as audio_file:
                            audio_file.write(question_audio.audio)
                        
                        transcribed_question = self.transcribe_with_whisper(audio_file_path)

                        await self.on_incoming_call(call, transcribed_question, result)
                else:
                    sw_logger.info('\n--- Continue Call ---')
                    call_id = result.event.payload.get('call_id')
                    from_phone = result.event.payload.get('device').get('params').get('from_number')
                    
                    sw_logger.info(f'\nfrom phone: {from_phone} \nquestion: {question}')

                    history = Call.get_by_session_id(call_id)
                    
                     # Use a thread to run qa_chain to avoid blocking the main event loop
                    loop = asyncio.get_event_loop()
                    answer = await loop.run_in_executor(None, qa_chain, question, history)
                    
                    Call.create(from_phone=from_phone, session_id=call_id, question=question, answer=answer)

                    sw_logger.info(f'\nanswer: {answer}\n')
                    
                    question_audio = await call.prompt_tts(prompt_type='speech', text=answer, speech_language='en-US')
                    audio_file_path = "./question.wav"
                    with open(audio_file_path, "wb") as audio_file:
                        audio_file.write(question_audio.audio)
                    
                    transcribed_question = self.transcribe_with_whisper(audio_file_path)

                    await self.on_incoming_call(call, transcribed_question, result)
            
        except Exception as e:
            sw_logger.error('Error Making Calls: %s', str(e))
            sw_logger.error(traceback.format_exc())
            pass
    
    def transcribe_with_whisper(self, audio_file_path):
        result = model.transcribe(audio_file_path)
        return result['text']
# Run your consumer..
consumer = CustomConsumer()
consumer.run()