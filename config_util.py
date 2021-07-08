from google.auth.transport import requests as google_requests
from google.oauth2 import service_account
import uuid

def setup_cx_google_config():
    '''
    Method to setup google api config
    '''
    CRED_SCOPE = ["https://www.googleapis.com/auth/cloud-platform"]
    CRED_KEY_PATH = 'secret_key.json' # this is also is not yet valid key for the project
    credentials = service_account.Credentials.from_service_account_file(
        CRED_KEY_PATH, scopes=CRED_SCOPE
    )

    if credentials.expired:
        credentials.refresh(google_requests.Request())
    
    bearer_token = credentials.token

    # ini bisa disimpen di db unique tiap whatsapp number (kalo belom ada) 
    # kalo udah ada, query dari db
    # implementation soon
    session_id = uuid.uuid4()

    return (bearer_token, session_id)