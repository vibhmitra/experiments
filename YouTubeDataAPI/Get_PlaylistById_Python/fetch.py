# This is just a simple script that grabs list from a youtube playlist using YouTube Data API. ➕
# It will try to get youtube video title and publishedAt time. 📺
# PlaylistID and an API Key is needed. 💁
# [NOTE] It only will grab Public Playlist as you will need OAuth Stuff to access private stufffs.

import requests
import dotenv
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
# Get API key and playlist ID from environment variables
API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = os.getenv("YOUTUBE_PLAYLIST_ID")
BASE_URL = os.getenv("YOUTUBE_API_URL")

params = {
    "part": "snippet",
    "playlistId": PLAYLIST_ID,
    "maxResults": 50,  # Max allowed per request
    "key": API_KEY
}

videos = []
next_page_token = None

# Fetch all videos using pagination
while True:
    if next_page_token:
        params["pageToken"] = next_page_token
    
    response = requests.get(BASE_URL, params=params).json()
    
    for item in response.get("items", []):
        title = item["snippet"]["title"]
        added_date = item["snippet"]["publishedAt"]
        videos.append(f"{title} - Added on {added_date}")
    
    next_page_token = response.get("nextPageToken")
    
    if not next_page_token:
        break  # No more pages to fetch

# Save results to a simple text file
with open("playlist_videos.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(videos))

print("✅ Playlist successfully saved to playlist_videos.txt")

