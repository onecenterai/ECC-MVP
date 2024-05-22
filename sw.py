import asyncio
from signalwire.relay.consumer import Consumer
import os
from app.call.model import Call
from helpers.langchain import qa_chain
from app import app


class CustomConsumer(Consumer):
    def setup(self):
        self.project = os.getenv('SW_PROJECT_ID')
        self.token = os.getenv("SW_TOKEN")
        self.contexts = ['ecc-mvp']
    
    async def on_incoming_call(self, call, question="Hello", result=None):
        try:
            with app.app_context():
                if not result:
                    print('New Call')
                    result = await call.answer()
                    if result.successful:
                        call_id = result.event.payload.get('call_id')
                        from_phone = result.event.payload.get('device').get('params').get('from_number')
                        
                                                    
                        answer = f'Hello, welcome to the Emergercy Hotline! How may I assist you today?'
                        Call.create(from_phone, call_id, question, answer)
                        question = await call.prompt_tts(prompt_type='speech', text=answer)
                        await self.on_incoming_call(call, question.result, result)
                else:
                    print('Continued Call')
                    call_id = result.event.payload.get('call_id')
                    from_phone = result.event.payload.get('device').get('params').get('from_number')

                    history = Call.get_by_session_id(call_id)
                    answer = qa_chain(question, history)

                    history = Call.get_by_session_id(call_id)
                    answer = qa_chain(question, history)
                    Call.create(from_phone, call_id, question, answer)
                    question = await call.prompt_tts(prompt_type='speech', text=answer)
                    await self.on_incoming_call(call, question.result, result)
        except Exception as e:
            print(e)
            pass

# Run your consumer..
consumer = CustomConsumer()
consumer.run()