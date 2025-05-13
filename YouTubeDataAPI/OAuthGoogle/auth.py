from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

scopes = ["https://www.googleapis.com/auth/youtube"]
client_secret_file = "client_shush.json")
   
flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)

flow.run_local_server(prompt="consent", open_browser=False)
credentials = flow.credentials

print(credentials.to_json())
