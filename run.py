# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""

    #Try adding your own number to this list
    callers = {
        "+16106083377": "Jon Kearney"
    }
    from_number = request.values.get('From', None)
    message = callers[from_number] if from_number in callers else "Monkey"
    resp = MessagingResponse()
    resp.message("{}, thanks for the message!".format(message))
    #resp.message("Hello, Mobile Monkey")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
