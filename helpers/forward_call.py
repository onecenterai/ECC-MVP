# from signalwire.relay.client import Client
# from signalwire.voice_response import VoiceResponse, Dial
# import os
# from dotenv import load_dotenv

# load_dotenv()

# client = Client(project=os.getenv('SW_PROJECT_ID'), token=os.getenv("SW_TOKEN"))


# #async def forward(caller, agency):
# async def forward():
#     try:
#         call = client.calling.new_call(from_number='+2349067887538', to_number='+2348037224859')
#         result = await call.connect() #this is it!!

#         if result.successful:
#             print('Call Answered')
#         else:
#             print(vars(result.component))
#             print('Call Failed')
#         return True
#     except Exception as e:
#         print(e)
#         return False

        
    

# import asyncio

# asyncio.run(forward())

