import asyncio
from signalwire.relay.consumer import Consumer
import os
from app.call.model import Call
from helpers.langchain import qa_chain
from app import app
from logger import log

class CustomConsumer(Consumer):
    def setup(self):
        self.project = os.getenv('SW_PROJECT_ID')
        self.token = os.getenv("SW_TOKEN")
        self.contexts = ['ecc-mvp']
    
    async def on_incoming_call(self, call, question="Hello", result=None):
        try:
            with app.app_context():
                if not result:
                    log.info('\n\n--- New Call ---')
                    result = await call.answer()
                    if result.successful:
                        call_id = result.event.payload.get('call_id')
                        from_phone = result.event.payload.get('device').get('params').get('from_number')
                                                    
                        answer = f'ECC, What is your Emergency?'
                        Call.create(from_phone=from_phone, session_id=call_id, question=question, answer=answer)

                        log.info(f'\nfrom phone: {from_phone} \nquestion: {question} \nanswer: {answer}\n')

                        question = await call.prompt_tts(prompt_type='speech', text=answer, speech_language='en-US')

                        await self.on_incoming_call(call, question.result, result)
                else:
                    log.info('\n--- Continue Call ---')
                    call_id = result.event.payload.get('call_id')
                    from_phone = result.event.payload.get('device').get('params').get('from_number')

                    history = Call.get_by_session_id(call_id)
                    answer = qa_chain(question, history)
                    
                    Call.create(from_phone=from_phone, session_id=call_id, question=question, answer=answer)

                    log.info(f'\nfrom phone: {from_phone} \nquestion: {question} \nanswer: {answer}\n')
                    
                    question = await call.prompt_tts(prompt_type='speech', text=answer)
                    await self.on_incoming_call(call, question.result, result)
        except Exception as e:
            print(e)
            pass

# Run your consumer..
consumer = CustomConsumer()
consumer.run()