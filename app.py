''''
DialogFlow x WhatsApp Integration
Using Twilio and DialogFlow ES/CX API
'''

from flask import Flask, request, session
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from google.api_core.exceptions import InvalidArgument
from config_util import setup_cx_google_config
import os
import dialogflow_v2
import requests
import json

# Twilio config
account_sid = os.getenv('account_sid')  
auth_token = os.getenv('auth_token')
client = Client(account_sid, auth_token)

# DF Config (API not activated)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'secret_key.json' # Secret key is not yet correct (project is wrong)
DF_PROJECT_ID = os.getenv('project_id')
DF_LANGUAGE_CODE = 'en'

# Flask Config
app = Flask(__name__)
app.secret_key = "it's a secret!"

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello World"


@app.route('/es', methods=["POST"])
def reply_using_es():
    SESSION_ID = "test" # ini bisa disimpen di db unique untuk tiap no.hp

    session_client = dialogflow_v2.SessionsClient()
    session = session_client.session_path(DF_PROJECT_ID, SESSION_ID)

    message = request.form['Body']
    txt_input = dialogflow_v2.types.TextInput(text=message, language_code = DF_LANGUAGE_CODE)
    query_input = dialogflow_v2.types.QueryInput(text=txt_input)

    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise

    # print("Query text:", response.query_result.query_text)
    # print("Detected intent:", response.query_result.intent.display_name)
    # print("Detected intent confidence:", response.query_result.intent_detection_confidence)
    # print("Fulfillment text:", response.query_result.fulfillment_text)

    twilio_resp = MessagingResponse()
    twilio_resp.message(response.query.result.fulfillment_text)

    return str(twilio_resp)


@app.route('/cx', methods=["POST"])
def reply_using_cx():
    bearer_token, session_id = setup_cx_google_config()
    message = request.form['Body']
    project_id = os.environ.get('project_id')
    location_id = os.environ.get('location_id')
    agent_id = os.environ.get('agent_id')

    url = f'''
    https://dialogflow.googleapis.com/v3/projects/{project_id}/locations/{location_id}/agents/{agent_id}/sessions/{session_id}:detectIntent
    '''

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization':'Bearer ' + bearer_token
    }

    data = {
        "queryInput": {
            "languageCode": "en",
            "text": {
                "text": message
            }
        },
        "queryParams": {
            "timeZone": "Asia/Jakarta"
        }
    }

    post_data = json.dumps(data)
    response = requests.post(url=url, headers=headers, data=post_data)
    print(response.text)
        
    result = json.loads(response.text)
    resp_msg = result['queryResult']['responseMessages']
    # resp_json = json.dumps(resp_msg)

    twilio_resp = MessagingResponse()
    twilio_resp.message(resp_msg)

    return str(twilio_resp)


def test_send_message():
    '''
    Test sending message from twilio to whatsapp
    future-purpose: hangout integration
    hangout-twilio-whatsapp
    '''

    client.messages.create(
        to="whatsapp:+6287888893902",
        from_="whatsapp:+14155238886",
        body="test send using twilio api method"
    )


if __name__ == "__main__":
    test_send_message()
    print("success")
    app.run(debug=True, port=9000)
    