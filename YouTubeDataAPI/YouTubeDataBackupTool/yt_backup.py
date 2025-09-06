#!/usr/bin/env python3
# yt_backup.py

import os
import json
import time
import sqlite3
import logging
# import shutil
from pathlib import Path
from functools import wraps
from datetime import datetime, timezone

import click
from tqdm import tqdm
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

# Constants

BASE_PATH = Path(__file__).parent.resolve()
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
CREDENTIALS_FILE = Path('secret/client_secrets_vi.json').resolve()
TOKEN_DIR = Path('tokens').resolve()
LOG_FILE = Path('logs/yt_backup.log').resolve()
EXPORT_PATH = Path('exports').resolve()         # Ineffective since export path is explicitly set per user in export()
USER_DATA_DIR = BASE_PATH / "backups"           # customizable user data root directory


# Setup User Directories

def setup_user_directories(user_id: str) -> None:
    """Create directory structure for a new user."""
    # user_base = Path('users') / user_id
    # user_base = BASE_PATH / Path('users') / user_id
    user_base = USER_DATA_DIR / user_id
    directories = {
        'backup_db': user_base / 'backup_db',
        'exports': user_base / 'exports'
    }
    for dir_path in directories.values():
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f'Created directory: {dir_path}')
    

# Setup logging

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Helpers

def retry_on_errors(max_retries=5, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = 1
            for attempt in range(1, max_retries+1):
                try:
                    return func(*args, **kwargs)
                except HttpError as e:
                    status = getattr(e.resp, 'status', None)
                    if status in (403, 500, 503):
                        logger.warning(f'HTTP {status} on {func.__name__}, retry {attempt}/{max_retries}')
                        time.sleep(delay)
                        delay *= backoff_factor
                        continue
                    raise
            raise RuntimeError(f'Failed after {max_retries} attempts: {func.__name__}')
        return wrapper
    return decorator

# Main Backup Class

class YouTubeBackup:
    def __init__(self, user_id: str):
        self.user_id = user_id
        # Create user directories first
        setup_user_directories(self.user_id)
        # Update DB_FILE path to use the user-specific path
        # self.db_file = Path('users') / user_id / 'backup_db' / 'youtube_backup.db'
        self.db_file = USER_DATA_DIR / user_id / 'backup_db' / 'youtube_backup.db'
        self.creds = self._load_or_create_credentials()
        self.youtube = build('youtube', 'v3', credentials=self.creds, cache_discovery=False)
        self.conn = sqlite3.connect(self.db_file)
        self._init_db()    

    def _load_or_create_credentials(self) -> Credentials:
        TOKEN_DIR.mkdir(exist_ok=True)
        token_path = TOKEN_DIR / f'{self.user_id}.json'

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                print(creds)
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
            return creds

        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=0, open_browser=False)
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
        return creds

    def _init_db(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id TEXT, channel_id TEXT PRIMARY KEY, title TEXT, description TEXT, published_at TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            user_id TEXT, playlist_id TEXT PRIMARY KEY, title TEXT, description TEXT,
            item_count INTEGER, privacy_status TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY, title TEXT, description TEXT,
            channel_title TEXT, published_at TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS playlist_items (
            playlist_id TEXT, video_id TEXT, position INTEGER, added_at TEXT,
            PRIMARY KEY (playlist_id, video_id)
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS sync_meta (
            playlist_id TEXT PRIMARY KEY,
            last_count INTEGER,
            last_sync_time TEXT,
            last_etag TEXT,
            last_updated_time TEXT
        )""")
        self.conn.commit()

    def _paginate(self, resource, **kwargs):
        request = getattr(self.youtube, resource)().list(**kwargs)
        while request:
            resp = request.execute()
            for item in resp.get('items', []):
                yield item
            request = getattr(self.youtube, resource)().list_next(request, resp)

    @retry_on_errors()
    def fetch_subscriptions(self):
        logger.info(f'Fetching subscriptions for {self.user_id}')
        c = self.conn.cursor()
        for sub in tqdm(self._paginate(
            'subscriptions',
            part='snippet,contentDetails',
            mine=True,
            maxResults=50
        ), desc='Subscriptions'):
            data = sub['snippet']
            c.execute("""
            INSERT OR REPLACE INTO subscriptions
            (user_id, channel_id, title, description, published_at)
            VALUES (?, ?, ?, ?, ?)
            """, (
                self.user_id,
                data['resourceId']['channelId'],
                data['title'],
                data.get('description', ''),
                data['publishedAt']
            ))
        self.conn.commit()

    @retry_on_errors()
    def fetch_playlists(self):
        logger.info(f'Fetching playlists for {self.user_id}')
        c = self.conn.cursor()
        for pl in tqdm(self._paginate(
            'playlists',
            part='snippet,contentDetails,status',
            mine=True,
            maxResults=50
        ), desc='Playlists'):
            snip = pl['snippet']
            cd = pl['contentDetails']
            st = pl['status']
            c.execute("""
            INSERT OR REPLACE INTO playlists
            (user_id, playlist_id, title, description, item_count, privacy_status)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.user_id,
                pl['id'],
                snip['title'],
                snip.get('description',''),
                cd.get('itemCount', 0),
                st.get('privacyStatus','public')
            ))
        self.conn.commit()

    def _should_fetch_playlist(self, playlist_id, new_count, current_etag=None, updated_time=None):
        c = self.conn.cursor()
        c.execute("""
            SELECT last_count, last_sync_time, last_etag, last_updated_time 
            FROM sync_meta 
            WHERE playlist_id=?""", (playlist_id,))
        row = c.fetchone()

        if row is None:
            logger.info(f'First sync for playlist {playlist_id}')
            return True

        last_count, last_sync_time, last_etag, last_updated_time = row

        # Check etag if available
        if current_etag and last_etag:
            if current_etag != last_etag:
                logger.info(f'Playlist {playlist_id} etag changed, needs sync')
                return True

        # Check update timestamp if available
        if updated_time and last_updated_time:
            try:
                last_updated = datetime.fromisoformat(last_updated_time.replace('Z', '+00:00'))
                current_updated = datetime.fromisoformat(updated_time.replace('Z', '+00:00'))
                if current_updated > last_updated:
                    logger.info(f'Playlist {playlist_id} has newer update timestamp')
                    return True
            except ValueError as e:
                logger.warning(f'Error comparing timestamps for {playlist_id}: {e}')

        # Fall back to count comparison
        if new_count > last_count:
            logger.info(f'Playlist {playlist_id} item count increased from {last_count} to {new_count}')
            return True

        logger.info(f'Playlist {playlist_id} is up to date')
        return False

    @retry_on_errors()
    def fetch_playlist_items(self, playlist_id):
        logger.info(f'Fetching items for playlist {playlist_id}')
        c = self.conn.cursor()
        
        # Get playlist metadata from YouTube API
        playlist_response = self.youtube.playlists().list(
            part='snippet,contentDetails',
            id=playlist_id
        ).execute()
        
        if not playlist_response.get('items'):
            logger.warning(f'Playlist {playlist_id} not found or not accessible')
            return
            
        playlist = playlist_response['items'][0]
        current_etag = playlist_response.get('etag')
        total = playlist['contentDetails'].get('itemCount', 0)
        updated_time = playlist['snippet'].get('publishedAt')
        
        if not self._should_fetch_playlist(playlist_id, total, current_etag, updated_time):
            logger.info(f'No changes detected in playlist {playlist_id}')
            return

        # Start transaction for atomic updates
        self.conn.execute("BEGIN TRANSACTION")
        try:
            # Clear all existing positions for this playlist
            c.execute("""
                DELETE FROM playlist_items 
                WHERE playlist_id = ?
            """, (playlist_id,))
            
            new_count = 0
            for item in tqdm(self._paginate(
                'playlistItems',
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=50
            ), desc=f'Items {playlist_id}'):
                vid = item['contentDetails']['videoId']
                vsnip = item['snippet']
                
                # Insert or update video record
                c.execute("""
                INSERT OR REPLACE INTO videos
                (video_id, title, description, channel_title, published_at)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    vid,
                    vsnip['title'],
                    vsnip.get('description',''),
                    vsnip.get('videoOwnerChannelTitle',''),
                    item['contentDetails']['videoPublishedAt']
                ))
                
                # Insert playlist item with current position
                c.execute("""
                INSERT OR REPLACE INTO playlist_items
                (playlist_id, video_id, position, added_at)
                VALUES (?, ?, ?, ?)
                """, (
                    playlist_id,
                    vid,
                    vsnip['position'],
                    vsnip['publishedAt']
                ))
                new_count += 1
                
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f'Error updating playlist items: {e}')
            raise

        # update sync_meta with all tracking information
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
        INSERT OR REPLACE INTO sync_meta 
        (playlist_id, last_count, last_sync_time, last_etag, last_updated_time)
        VALUES (?, ?, ?, ?, ?)
        """, (
            playlist_id,
            total,
            now,
            current_etag,
            updated_time or now
        ))
        self.conn.commit()
        logger.info(f'Fetched {new_count} new items for {playlist_id}')

    @retry_on_errors()
    def fetch_special_playlists(self):
        """Fetch 'Liked videos' and 'Watch Later' playlists."""
        logger.info(f'Fetching special playlists for {self.user_id}')
        c = self.conn.cursor()
        
        special_playlists = {
            'LL': ('Liked videos', 'liked'),
            'WL': ('Watch Later', 'watchLater')
        }
        
        for playlist_key, (title, playlist_type) in special_playlists.items():
            try:
                # Get playlist items directly using channels.playlistItems
                items_request = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_key,
                    maxResults=50
                )
                
                # First try to get at least one item to verify access
                response = items_request.execute()
                total_items = response.get('pageInfo', {}).get('totalResults', 0)
                
                # Add to playlists table
                c.execute("""
                INSERT OR REPLACE INTO playlists
                (user_id, playlist_id, title, description, item_count, privacy_status)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.user_id,
                    playlist_key,
                    title,
                    f'System playlist: {title}',
                    total_items,
                    'private'
                ))
                
                # Process all items
                for item in self._paginate('playlistItems',
                    part='snippet,contentDetails',
                    playlistId=playlist_key,
                    maxResults=50
                ):
                    vid = item['contentDetails']['videoId']
                    vsnip = item['snippet']
                    
                    # Insert video record
                    c.execute("""
                    INSERT OR IGNORE INTO videos
                    (video_id, title, description, channel_title, published_at)
                    VALUES (?, ?, ?, ?, ?)
                    """, (
                        vid,
                        vsnip['title'],
                        vsnip.get('description', ''),
                        vsnip.get('videoOwnerChannelTitle', ''),
                        item['contentDetails'].get('videoPublishedAt', '')
                    ))
                    
                    # Insert playlist item
                    c.execute("""
                    INSERT OR IGNORE INTO playlist_items
                    (playlist_id, video_id, position, added_at)
                    VALUES (?, ?, ?, ?)
                    """, (
                        playlist_key,
                        vid,
                        vsnip['position'],
                        vsnip['publishedAt']
                    ))
                
                self.conn.commit()
                logger.info(f'Fetched {total_items} items from {title}')
                
            except HttpError as e:
                if e.resp.status in (403, 404):
                    logger.warning(f'No access to {title} playlist')
                else:
                    raise

    def sync_all(self):
        self.fetch_subscriptions()
        self.fetch_playlists()
        self.fetch_special_playlists()
        # fetch items per playlist
        c = self.conn.cursor()
        for (plid,) in c.execute(
            "SELECT playlist_id FROM playlists WHERE user_id=?", (self.user_id,)
        ):
            self.fetch_playlist_items(plid)

    def export(self, fmt='csv', export_path=EXPORT_PATH):
        import csv
        # Get current timestamped directory
        now_str = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        out_dir = os.path.join(export_path, now_str)
        os.makedirs(out_dir, exist_ok=True)
        export_path = out_dir

        tables = ['subscriptions', 'playlists', 'videos', 'playlist_items']
        for tbl in tables:
            c = self.conn.cursor()
            c.execute(f"SELECT * FROM {tbl}")
            rows = c.fetchall()
            cols = [d[0] for d in c.description]

            if fmt == 'csv':
                file_name = f'{self.user_id}_{tbl}.csv'
                fp = os.path.join(export_path, file_name)
                print(f"Saving :{export_path}")
                with open(fp, 'w', newline='', encoding='utf8') as f:
                    writer = csv.writer(f)
                    writer.writerow(cols)
                    writer.writerows(rows)
                logger.info(f'Exported {tbl} → {fp}')
            else:
                file_name = f'{self.user_id}_{tbl}.json'
                fp = os.path.join(export_path, file_name)
                data = [dict(zip(cols, row)) for row in rows]
                with open(fp, 'w', encoding='utf8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f'Exported {tbl} → {fp}')            

    def close(self):
        self.conn.close()

# CLI Commands

@click.group()
def cli():
    """YouTube Data Backup CLI."""
    pass

@cli.command()
@click.argument('user_id')
def login(user_id):
    """Authorize a user and store tokens."""
    YouTubeBackup(user_id)
    click.echo(f'User {user_id} logged in and token stored.')

@cli.command()
@click.argument('user_id')
def sync(user_id):
    """Fetch and sync YouTube data."""
    backup = YouTubeBackup(user_id)
    backup.sync_all()
    backup.close()
    click.echo(f'Sync complete for {user_id}.')

@cli.command()
@click.argument('user_id')
@click.option('--format', 'fmt', type=click.Choice(['csv','json']), default='csv')
def export(user_id, fmt):
    """Export backed-up data to CSV or JSON."""
    backup = YouTubeBackup(user_id)
    backup.export(fmt, export_path=USER_DATA_DIR / user_id / 'exports')
    backup.close()
    click.echo(f'Exported data for {user_id} in {fmt} format.')

@cli.command()
def users():
    """List all authorized users."""
    TOKEN_DIR.mkdir(exist_ok=True)
    us = [p.stem for p in TOKEN_DIR.glob('*.json')]
    click.echo('Authorized users:')
    for u in us:
        click.echo('  - ' + u)

if __name__ == '__main__':
    cli()

## A Fucntion to list users with expiry dates - I commented out it for simplicity 

# def users():
#     """List all authorized users with their expiry dates."""
#     TOKEN_DIR.mkdir(exist_ok=True)
#     user_files = [p for p in TOKEN_DIR.glob('*.json')]
#     click.echo('Authorized users:')
#     for user_file in user_files:
#         user_name = user_file.stem
#         expiry_date = 'Unknown'
#         try:
#             with open(user_file, 'r') as f:
#                 data = json.load(f)
#                 if 'expiry' in data:
#                     expiry_date = data['expiry']
#         except Exception as e:
#             expiry_date = f'Error reading expiry: {e}'

        # click.echo(f'  - {user_name} (Expiry: {expiry_date})')
