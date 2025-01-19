from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.params import Query
import requests
import os

app = FastAPI()

client_id = "0480bfb577374efc9f573a66a71fc225"  # Replace with your Spotify client ID
client_secret = "e7964bcb1dfd4e6f8cd9d90a73c9ac8e"  # Replace with your Spotify client secret
redirect_uri = 'http://localhost:8000/callback'  # Make sure this is the same as in your Spotify app

# Step 1: Generate the Authorization URL
@app.get("/")
def home():
    auth_url = (
        f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code"
        f"&redirect_uri={redirect_uri}&scope=user-top-read"
    )
    return HTMLResponse(f'<a href="{auth_url}">Click here to login with Spotify</a>')

# Step 2: Handle the Callback from Spotify
@app.get("/callback")
def callback(code: str = Query(...)):
    # Step 3: Exchange the authorization code for an access token
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        if access_token:
            return {"access_token": access_token}
        else:
            return {"error": "Access token not found"}
    else:
        return {"error": response.json()}

# Step 4: Get Top Tracks (example function)
@app.get("/top-tracks/{artist_id}")
def get_top_tracks(artist_id: str, access_token: str):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "market": "US"
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        top_tracks = response.json().get("tracks", [])
        return {"top_tracks": [track['name'] for track in top_tracks]}
    else:
        return {"error": response.json()}

@app.get("/available-markets")
def get_available_markets(access_token: str):
    url = "https://api.spotify.com/v1/markets"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        markets = response.json().get("markets", [])
        return {"available_markets": markets}
    else:
        return {"error": response.json()}
