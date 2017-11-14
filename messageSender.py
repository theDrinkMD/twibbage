import os
from twilio.rest import Client

def sendMessage(to, m):
    #send out questions
    ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    print("Sending Message:{} \r To: {}".format(m, to))
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    message = client.messages.create(
            to,
            body=m,
            from_="+12566678942")

    print(message.sid)
