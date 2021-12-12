import os
from sys import argv
import re
import googleapiclient.errors
import googleapiclient.discovery
import google_auth_oauthlib.flow
from spotipy.oauth2 import SpotifyOAuth
import spotipy

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.


def clean_up_song_names(song: str):
    subs = [
        r"\(.+\)", r"\[.+\]",
        r"(ft\.|Feat\.)[0-9A-za-z, ]*",
        r"[|][0-9A-ZA-z ]*",
        r"[,][0-9A-ZA-z\., ]*",
        r"[&][0-9A-ZA-z\., ]*",
        "Official Video",
        "Official Audio"
    ]

    for sub in subs:
        song = re.sub(sub, '', song)

    return song


playlist_name = ''
public_playlist = False
playlist_description = ''
song_names = []

yt_playlist_id = ''
yt_scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

sp = None
current_user = None

try:
    # Spotify commandline arguments
    playlist_name, public_playlist, playlist_description = argv[1], argv[2], argv[3]

    # Test songs
    song_names = [
        'The Weend - Die for you',
        'Doja Cat - Kiss me More',
        'Kanye West - Slow Jamz',
    ]

    # Youtube commmandline arguments
    yt_playlist_id = argv[4]
except Exception as e:
    print("Commandline Arguments were not set!")
    print(f"Error: {e}")


# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python


try:
    # Youtube stuff
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, yt_scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=100,
        playlistId=yt_playlist_id
    )
    response = request.execute()

    song_names = [clean_up_song_names(
        item["snippet"]["title"]) for item in response["items"]]
except Exception as e:
    print("An error occured when trying to access youtube")
    print(f"Error: {e}")

try:
    # User Spotify Authentication
    SCOPE = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))
    current_user = sp.current_user()
except Exception as e:
    print("An error occured when trying to authenticate user on spotify")
    print(f"Error: {e}")

try:
    # Creating and adding songs to spotify playlist
    result = sp.user_playlist_create(current_user['id'], playlist_name,
                                     public_playlist, False, playlist_description)
    playlist_id = result['id']
    song_ids = []
    for song in song_names:
        try:
            print(f"Adding - {song}")
            song_info = sp.search(song, type='track')
            song_ids.append(song_info['tracks']['items'][0]['id'])
        except Exception as e:
            print(f"{song} was not added")
            print(f"Error: {e}")
            print("")

    # song_ids = [sp.search(song, type='track')['tracks']
    # ['items'][0]['id'] for song in song_names]

    print(f"Adding all songs to Spotify Playlist {playlist_name}")
    add_playlist_songs_result = sp.playlist_add_items(playlist_id, song_ids)
except Exception as e:
    print("An error occured while trying to create new user playlist")
    print(f"Error: {e}")
