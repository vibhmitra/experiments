# Import necessary libraries
import os
import json
import pickle
from arrow import get
from dotenv import dotenv_values

from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow  # for manual auth
from google.auth.transport.requests import Request

# LOAD ENVIRONMENT VARIABLES
ENV = dotenv_values('.env')

# Set up the path to the client secrets file
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), ENV['CLIENT_SECRETS_JSON'])
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
TOKEN_CREDS = 'token_v.pickle'


def load_credentials():
    if os.path.exists(TOKEN_CREDS):
        creds = read_credentials()
        return creds
    else:
        return get_authenticated_manually()


# Oauth Flow | Auto (docs: https://googleapis.github.io/google-api-python-client/docs/oauth.html)
def get_authenticated():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    auth_url, _ = flow.authorization_url()
    creds = flow.run_local_server(open_browser=False)
    print(creds.to_json())
    write_credentials(creds)
    return creds

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
    creds = load_credentials()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print('Refreshing Access Token...')
            creds.refresh(Request())
        else:
            creds = get_authenticated_manually()
            write_credentials(creds)
    return creds

# 📞
# get_authenticated_service()
# get_authenticated_manually()

get_credentials()