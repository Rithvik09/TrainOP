import os
import io
import json
import urllib
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

call = client.calls.create(
                        twiml='<Response><Say>nikku nikku nikku do not think we are forgetting about you because we are not calling you. Just know, you are never safe, no matter who you have with you.</Say></Response>',
                        to=os.environ['TWILIO_TO_NUMBER'],
                        from_=os.environ['TWILIO_FROM_NUMBER']
                    )

print(call.sid)
