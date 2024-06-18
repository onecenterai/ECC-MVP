import asyncio
from signalwire.relay.consumer import Consumer
import os
from app.call.model import Call
from helpers.langchain import qa_chain
from app import app
from logger import sw_logger
import traceback
import socketio


# import whisper
# model = whisper.load_model("base")

sio = socketio.Client()
sio.connect('http://localhost:3000')

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

                        #await self.forward(call=call)
                                                    
                        answer = f'ECC, What is your Emergency?'
                        Call.create(from_phone=from_phone, session_id=call_id, question=question, answer=answer)

                        sw_logger.info(f'\nfrom phone: {from_phone} \nquestion: {question} \nanswer: {answer}\n')

                        question = await call.prompt_tts(prompt_type='speech', text=answer, speech_language='en-US')

                        # push to ws endpoint
                        # await sio.emit('send_message', {'agent': answer, 'caller': question.result})

                        await self.on_incoming_call(call, question.result, result)
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
                    
                    question = await call.prompt_tts(prompt_type='speech', text=answer, speech_language='en-US')

                    # push to ws endpoint
                    # await sio.emit('send_message', {'agent': answer, 'caller': question.result})

                    await self.on_incoming_call(call, question.result, result)
            
        except Exception as e:
            sw_logger.error('Error Making Calls: %s', str(e))
            sw_logger.error(traceback.format_exc())
            pass
        finally:
            sio.disconnect()

    
    # def transcribe_with_whisper(self, audio_file_path):
    #     result = model.transcribe(audio_file_path)
    #     return result['text']

    async def prompt_and_record(self, call, text):
        # recording = await call.record_async(
        #     stereo=True
        # )
        # print(vars(recording))
        # print('\n\n')
        # print(dir(recording))
        # if not recording.successful:
        #     sw_logger.error(f"Failed to start recording: {recording}")
        #     #return


        customer_response = await call.prompt_tts(prompt_type='speech', text=text, speech_language='en-US')
        print(customer_response.result)

        # await recording.stop()

        # print(f'\nrecording url: {recording.url}\n')

        # audio_file_path = "./question.wav"
        # with open(audio_file_path, "wb") as audio_file:
        #     audio_file.write(recording.url)
        
        #transcribed_question = self.transcribe_with_whisper(audio_file_path)

        return customer_response
    
    async def forward(self, call):
        try:
            result = await call.connect([{'to_number': '+2348037224859', 'timeout':10}]) #this is it!!

            if result.successful:
                print('Call Answered')
            else:
                print(vars(result.component))
                print('Call Failed')
            return True
        except Exception as e:
            print(e)
            return False


# Run your consumer..
consumer = CustomConsumer()
consumer.run()