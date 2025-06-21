# Import necessary libraries
import os
import pickle
import re
from dotenv import dotenv_values

from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow  # for manual auth
from google.auth.transport.requests import Request

from utils import get_tokens, clear_console


# LOAD ENVIRONMENT VARIABLES
ENV = dotenv_values('.env')
KEY = ENV['YOUTUBE_API_KEY']

# Set up the path to the client secrets file
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), ENV['CLIENT_SECRETS_JSON'])
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
# TOKEN_CREDS = f"{ENV['CLIENT_SECRETS_JSON'].replace('.json', '_token.pickle')}"
TOKEN_CREDS = None

# Function to set the token credentials
def set_token_creds():
    global TOKEN_CREDS
    TOKEN_CREDS = get_tokens() or f"{os.path.dirname(__file__)}/token.pickle"

def load_credentials():
    if os.path.exists(TOKEN_CREDS):
        print(f"Loading Credentials from {TOKEN_CREDS}")
        creds = read_credentials()
        return creds
    else:
        return None

# Oauth Flow | Auto (docs: https://googleapis.github.io/google-api-python-client/docs/oauth.html)
def get_authenticated(manual_auth):
    if not manual_auth:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            auth_url, _ = flow.authorization_url()
            creds = flow.run_local_server(open_browser=False)
            print(creds.to_json())
        except Exception as error:
            print(f"[!] Authentication Failed\nError Code: {error}")
            return None
        
        write_credentials(creds)
        return creds
    else:
        get_authenticated_manually()

# Temporary function to get the auth code manually
def get_authenticated_manually():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, redirect_uri="http://localhost:8080")
    auth_url, _ = flow.authorization_url()
    print(f'Please go to this URL: {auth_url}')
    code = input('Enter the authorization code: ')
    flow.fetch_token(code=code)
    creds = flow.credentials
    print(creds.to_json())
    write_credentials(creds)
    return creds

# Write Credentials to a file
def write_credentials(creds):
    with open(TOKEN_CREDS, "wb") as token_file:
        pickle.dump(creds, token_file)

# Read Credentials from a file
def read_credentials():
    with open(TOKEN_CREDS, "rb") as token_file:
        creds = pickle.load(token_file)
    return creds


# Function to get the credentials
def get_credentials():
    set_token_creds()
    creds = load_credentials()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print('Refreshing Access Token...')
            creds.refresh(Request())
            print(f"New Token Expiry: {creds.expiry}\n")
            write_credentials(creds)
        else:
            print('No valid credentials available. Getting new credentials...')
            creds = get_authenticated(manual_auth=True)
    else:
        print(f"Using Old Token | Expiry: {creds.expiry}\n")
    return creds

# 📞
# get_authenticated_service()
# get_authenticated_manually()
# print(get_credentials().to_json())