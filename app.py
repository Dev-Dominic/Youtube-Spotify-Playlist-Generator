"""
    Converts a youtube playlist into a spotify playlist
"""

# Python libraries
import os
from sys import argv
from typing import Any, Union
import re

# Google SDK
import googleapiclient.errors
import googleapiclient.discovery
import google_auth_oauthlib.flow

# Spotify Third-party library
from spotipy.oauth2 import SpotifyOAuth
import spotipy

# Other Third-party libraries
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.


def clean_up_song_names(song: str) -> str:
    """
    Removes youtube specify keywords for a given song name

        Parameters:
            song (str): Youtube video song title

        Returns:
            song (str): mutated song name with extracted youtube video song
            title keywords and characters
    """
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


def google_auth() -> Any:
    """
    Returns object that can interface with google's API (youtube in this case)

        Parameters:
            yt_playlist_id (str): This is the public playlist id fo

        Returns:
            youtube (Any) : Google API instnace that allows for access to a user's
            youtube data.
    """
    try:
        # Youtube stuff
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secret_file = "client_secret.json"
        yt_scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secret_file, yt_scopes)
        credentials = flow.run_console()

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials)

        return youtube
    except Exception as exception:
        print("An error occured when trying to access youtube")
        print(f"Error: {exception}")


def yt_retrieve_playlist_items(yt_playlist_id: str, youtube) -> list[str]:
    """
    Returns a list containing all the songs present in a youtube playlist

        Parameters:
            yt_playlist_id (str): Youtube playlist public id
            youtube: Google API youtube isntance

        Returns:
            song_names (list[str]): List of song items present in youtube
            playlist
    """
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=100,
        playlistId=yt_playlist_id
    )
    response = request.execute()

    song_names = [clean_up_song_names(
        item["snippet"]["title"]) for item in response["items"]]

    return song_names


def spotify_auth() -> Any:
    """
    Authenticates a user and returns a Spotipy instance to access user playlist
    permission controls

        Returns:
            spotipy_instance (Any): Spotipy instance
    """
    try:
        scope = "playlist-modify-public"
        spotipy_instance = spotipy.Spotify(auth_manager=SpotifyOAuth(scope))

        return spotipy_instance
    except Exception as exception:
        print("An error occured when trying to authenticate user on spotify")
        print(f"Error: {exception}")


def create_spotify_playlist(
    spotipy_instance: spotipy.Spotify,
    playlist_name: str,
    public_playlist: bool,
    playlist_description: str,
    song_names: list[str]
) -> None:
    """
    Creates spotify playlist based
    """
    try:
        # Creating and adding songs to spotify playlist
        current_user: Any = spotipy_instance.current_user()
        result: Any = spotipy_instance.user_playlist_create(current_user['id'],
                                                            playlist_name,
                                                            public_playlist,
                                                            False,
                                                            playlist_description)

        playlist_id: str = result['id']
        song_ids = []
        for song in song_names:
            try:
                print(f"Adding - {song}")
                song_info: Any = spotipy_instance.search(song, type='track')
                song_ids.append(song_info['tracks']['items'][0]['id'])
            except Exception as exception:
                print(f"{song} was not added")
                print(f"Error: {exception}")

        print(f"Adding all songs to Spotify Playlist {playlist_name}")
        spotipy_instance.playlist_add_items(playlist_id, song_ids)
    except Exception as exception:
        print("An error occured while trying to create new user playlist")
        print(f"Error: {exception}")


def main():
    """Scrpt main function"""
    playlist_name: Union[str, None] = None
    public_playlist: bool = True
    playlist_description: Union[str, None] = None
    yt_playlist_id: Union[str, None] = None

    try:
        # Spotify commandline arguments
        playlist_name = argv[1]
        public_playlist = bool(argv[2])
        playlist_description = argv[3]

        # Youtube commmandline arguments
        yt_playlist_id = argv[4]
    except Exception as exception:
        print("Commandline Arguments were not set!")
        print(f"Error: {exception}")

    if None not in [playlist_name, playlist_description, yt_playlist_id]:
        youtube: Any = google_auth()
        spotify: Any = spotify_auth()

        # retrieve youtube playlist song items
        if yt_playlist_id is not None:
            youtube_playlist_songs = yt_retrieve_playlist_items(
                yt_playlist_id, youtube)
        # create spotify playlist using youtube playlist song items


if __name__ == "__main__":
    main()
