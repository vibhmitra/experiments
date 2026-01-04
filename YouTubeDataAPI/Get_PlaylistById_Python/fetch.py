# This is just a simple script that grabs list from a youtube playlist using YouTube Data API. ➕
# It will try to get youtube video title and publishedAt time., now Channel ID and name too. ;) 📺
# PlaylistID and an API Key is needed. 💁
# [NOTE] It only will grab Public Playlist as you will need OAuth Stuff to access private stufffs.

import requests
import dotenv
import os
import datetime
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
# Get API key and playlist ID from environment variables
API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = os.getenv("YOUTUBE_PLAYLIST_ID")
BASE_URL = os.getenv("YOUTUBE_API_URL")        # generally if querying public playlist data: https://www.googleapis.com/youtube/v3/playlistItems

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
        snippet = item["snippet"]
        title = snippet["title"]
        added_date = snippet["publishedAt"]
        channel_id = snippet.get("videoOwnerChannelId", "Unknown")         # 1. Get Channel ID
        channel_name = snippet.get("videoOwnerChannelTitle", "Unknown")     # 2. Get Channel Title
        
        # 3. Get Video ID and construct Full URL # Note: If using 'playlistItems', the ID is in snippet['resourceId']['videoId']
        resource = snippet.get("resourceId", {})
        video_id = resource.get("videoId")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Append the expanded info
        videos.append(f"{title} by {channel_name} | Channel URL: https://www.youtube.com/channel/{channel_id} | URL: {video_url} | Added On: {added_date}")
    
    next_page_token = response.get("nextPageToken")
    
    if not next_page_token:
        break  # No more pages to fetch

# Save results to a simple text file

timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
os.makedirs("backups", exist_ok=True)
filename = f"backups/playlist_videos_{timestamp}.txt"

with open(filename, "w", encoding="utf-8") as file:
    file.write("\n".join(videos))

print(f"✅ Playlist successfully saved to {filename}")
