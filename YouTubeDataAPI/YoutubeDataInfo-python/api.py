import os
import json
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from auth import get_credentials, load_credentials

creds = load_credentials()
youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

try:
    # Request the channel ID of the currently authorized user
    channel_response = youtube.channels().list(part="snippet,contentDetails,statistics", forHandle='@Qwerty').execute()
    # Extract the channel ID from the response
    channel_id = channel_response["items"][0]["id"]
    channel_title = channel_response["items"][0]["snippet"]["title"]
    published_at = channel_response["items"][0]["snippet"]["publishedAt"]

    print(f"Your channel ID: {channel_id}")
    print(f"Your channel title: {channel_title}")
    print(f"Your channel published at: {published_at}")

except HttpError as e:
    print(f"An error occurred: {e}")

except KeyError as e:
    print(f"Key error: {e}")

# request = youtube.playlists().list(
#         part="snippet,contentDetails",
#         channelId="channe_id",
#         maxResults=25
#     )
# response = request.execute()
# print(json.dumps(response, indent=4))