''''
DialogFlow x WhatsApp Integration method 1
Using Twilio and DialogFlow API
'''

import dialogflow_v2
from flask import Flask, request, session
from google.api_core.gapic_v1 import method
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
import dialogflow
import dialogflow_v2
from google.api_core.exceptions import InvalidArgument

# Twilio config
account_sid = os.getenv('account_sid')
auth_token = os.getenv('auth_token')
client = Client(account_sid, auth_token)

# DF Config (API not activated)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'secret_key.json' # Secret key is not yet correct (project is wrong)
DF_PROJECT_ID = "airy-torus-269506"
DF_LANGUAGE_CODE = 'en'

# Flask Config
app = Flask(__name__)
app.secret_key = os.environ.get('secret_key_flask')

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello World"


@app.route('/reply', methods=["POST"])
def reply():
    SESSION_ID = "test" # ini kayanya bisa disimpen di db untuk tiap no.hp

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DF_PROJECT_ID, SESSION_ID)
    print("session_id", SESSION_ID)

    message = request.form['Body']
    txt_input = dialogflow_v2.types.TextInput(text=message, language_code = DF_LANGUAGE_CODE)
    query_input = dialogflow_v2.types.QueryInput(text=txt_input)

    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise

    print("Query text:", response.query_result.query_text)
    print("Detected intent:", response.query_result.intent.display_name)
    print("Detected intent confidence:", response.query_result.intent_detection_confidence)
    print("Fulfillment text:", response.query_result.fulfillment_text)

    twilio_resp = MessagingResponse()
    twilio_resp.message(response.query.result.fulfillment_text)

    return str(twilio_resp)


if __name__ == "__main__":
    app.run(debug=True, port=9000)




