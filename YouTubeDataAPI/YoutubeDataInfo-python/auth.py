# Import necessary libraries
import os
import json
from dotenv import dotenv_values

from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow  # for manual auth

# LOAD ENVIRONMENT VARIABLES
ENV = dotenv_values('.env')

# Set up the path to the client secrets file
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), ENV['CLIENT_SECRETS_JSON'])
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Oauth Flow | Auto (docs: https://googleapis.github.io/google-api-python-client/docs/oauth.html)
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    auth_url, _ = flow.authorization_url()
    creds = flow.run_local_server(open_browser=False)
    print(creds.to_json())
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
    return creds


# 📞
# get_authenticated_service()
get_authenticated_manually()