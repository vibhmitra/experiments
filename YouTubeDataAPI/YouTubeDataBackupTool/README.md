# 🔴 YouTube Data Backup Tool 🔴

A Python-based command-line script / tool to backup your YouTube data including subscriptions, playlists, and video metadata. The script stores data locally in SQLite database and supports exporting to CSV/JSON formats.

## Features ✨

- Backup YouTube subscriptions
- Backup playlists (including private playlists)
- Backup playlist items and video metadata
- Multi-user support with isolated storage
- Export data to CSV or JSON formats
- Automatic token refresh for authentication
- Retry mechanism for API failures
- Progress tracking with tqdm
- Detailed logging

## Prerequisites 🕶️

- Python 3.7+
- Google API credentials (client_secret.json)
- Required Python packages (see Installation)

## Installation 🛠️

1. Clone the repository
2. Install required packages:
```bash
pip install google-auth-oauthlib google-api-python-client tqdm click
```
3. Place your `client_secret.json` in the `secret/` directory

## Directory Structure 📁

```
yt-data-bkp/
├── secret/
│   └── client_secret.json
├── tokens/
│   └── {user}.json
├── users/
│   └── {user_id}/
│       ├── backup_db/
│       │   └── youtube_backup.db
│       └── exports/
├── logs/
│   └── yt_backup.log
├── yt_backup.py
└── README.md
```

## Usage 🕹️

### First Time Setup

1. Login with your YouTube account:
```bash
python yt_backup.py login YOUR_USERNAME
```

### Basic Commands

1. Sync YouTube data:
```bash
python yt_backup.py sync YOUR_USERNAME
```

2. Export data:
```bash
python yt_backup.py export YOUR_USERNAME --format csv
```

3. List all users:
```bash
python yt_backup.py users
```

## Data Storage 💾

The tool stores data in SQLite databases with the following tables:
- subscriptions: YouTube channel subscriptions
- playlists: Playlist metadata
- videos: Video details
- playlist_items: Videos in playlists
- sync_meta: Synchronization metadata

## Error Handling 💢

- Automatic retries on API failures
- Detailed logging in logs/yt_backup.log
- Progress bars for long-running operations

## Security 🔒

- Uses OAuth 2.0 for authentication
- Supports multiple user accounts
- Read-only access to YouTube data

## License 📜

MIT License

## Contributing 🫰

Feel free to submit issues and enhancement requests!

## Disclaimer

This is not an official Google product. This application is for personal use and follows YouTube's terms of service.
