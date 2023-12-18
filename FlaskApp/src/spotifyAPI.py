import json
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPE = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))

def get_playlists(sp=sp, limit=50, offset=0):
    ''' Get user playlist given user'''
    playlists = sp.current_user_playlists(limit=limit, offset=offset)
    return playlists

def print_playlists(playlists, sp=sp):
    ''' Print all user playlists '''
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            print(f"{i + 1 + playlists['offset']:4d} {playlist['uri']} {playlist['name']}")
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None

def get_playlist_tracks(playlist_id, limit=100, offset=0):
    ''' Return tracks in a playlist given ID '''
    tracks = sp.playlist_tracks(playlist_id, limit=limit, offset=offset)
    return tracks

def print_playlist_tracks(tracks):
    ''' Print all tracks in playlist'''
    while tracks:
        for i, track in enumerate(tracks['items']):
            print(f"{i + 1 + tracks['offset']:4d} {track['track']['uri']} {track['track']['name']}")
        if tracks['next']:
            tracks = sp.next(tracks)
        else:
            tracks = None

# Query Docs: https://developer.spotify.com/documentation/web-api/reference/search
def search_spotify(search_artist,search_track):
    '''Search spotify given string inputs of artist and track'''

    #Formatting Inputs and Query
    search_artist = search_artist.replace(" ","%20")
    search_track = search_track.replace(" ","%20")
    query = f'q=track:{search_track}%20artist:{search_artist}' #ex: q=track:Royals%20artist:Lorde

    #Search Spotipy
    tracks = sp.search(query, limit=1, offset=0)['tracks']
    track_items = tracks['items'][0]
    external_url = track_items['external_urls']['spotify']
    track_uri = track_items['uri']
    
    print('query: ' + query)
    print('external_url: ' + external_url)
    print('track_uri: ' + track_uri)

search_spotify('Lorde','Royals') 
