import os
import json
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import auth

creds = auth.get_credentials()
youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

try:
    # Request the channel ID of the currently authorized user
    channel_response = youtube.channels().list(part="snippet,contentDetails,statistics", forHandle='@youtube').execute()
    
    # Extract Channel Metadata
    for item in channel_response["items"]:
        print(f"Channel ID: {item['id']}")
        print(f"Channel Title: {item['snippet']['title']}")
        print(f"Published At: {item['snippet']['publishedAt']}")
        print(f"Subscribers: {item['statistics']['subscriberCount']}")
        print(f"Total Views: {item['statistics']['viewCount']}")
        print(f"Total Videos: {item['statistics']['videoCount']}")
        print(f"Description: {item['snippet']['description']}")
        print(f"Thumbnail URL: {item['snippet']['thumbnails']['default']['url']}")
        print(f"Country: {item['snippet'].get('country', 'N/A')}")
        print(f"Custom URL: {item['snippet'].get('customUrl', 'N/A')}")
        print(f"Banner URL: {item['brandingSettings']['image']['bannerExternalUrl']}")
        print(f"Keywords: {item['brandingSettings']['channel']['keywords']}")



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