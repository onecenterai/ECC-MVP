
from pyngrok import ngrok
from dotenv import load_dotenv
import os

from twilio.rest import Client

twilio_client = Client()

port = 5000

load_dotenv()

ngrok.set_auth_token(os.getenv('NGROK_AUTHTOKEN'))
public_url = ngrok.connect(port, bind_tls=True).public_url

number = twilio_client.incoming_phone_numbers.list()[0]
number.update(voice_url=public_url + '/call/twilio/callback')

print(f'Waiting for calls on {number.phone_number}')