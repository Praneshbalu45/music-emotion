from flask import Flask, render_template_string
import cv2
import requests
import random
from deepface import DeepFace
import base64

app = Flask(__name__)

# Your Spotify API credentials
CLIENT_ID = '2c0f87f66f90428d85a464ac2c8d0136'
CLIENT_SECRET = 'd774df01daf445f2a84a364d6bba05e0'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Get Spotify access token
def get_spotify_token():
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response_data = response.json()
    return response_data['access_token']

def fetch_spotify_music_by_emotion(emotion):
    access_token = get_spotify_token()
    search_query = f'Tamil {emotion}'
    api_url = f'https://api.spotify.com/v1/search?q={search_query}&type=track&limit=10'
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        track_data = response.json()
        
        # Filter tracks longer than 4 minutes (240000 ms)
        long_tracks = []
        for item in track_data['tracks']['items']:
            if item['duration_ms'] > 240000:  # Check if the track is longer than 4 minutes
                long_tracks.append(item)
        
        return long_tracks
    except Exception as e:
        print(f"Error fetching music: {e}")
    return []

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Emotion Detection</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    background-color: #f0f4f8;
                    margin: 0;
                }
                h1 {
                    color: #333;
                }
                button {
                    padding: 10px 20px;
                    font-size: 16px;
                    color: white;
                    background-color: #007bff;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                button:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <h1>Emotion Detection and Music</h1>
            <button onclick="window.location.href='/capture'">Capture Emotion</button>
        </body>
        </html>
    ''')

@app.route('/capture')
def capture():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "Could not open webcam."

    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return "Could not read frame from webcam."

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=True)  # Set enforce_detection to True
    emotion = result[0]['dominant_emotion']
    
    # Fetch music tracks based on emotion
    tracks = fetch_spotify_music_by_emotion(emotion)

    # If no tracks found, try fetching any Tamil music
    if not tracks:
        print("No specific songs found for the detected emotion. Searching for general Tamil music...")
        tracks = fetch_spotify_music_by_emotion('music')

    if tracks:
        selected_track = random.choice(tracks)
        track_url = selected_track['external_urls']['spotify']
        track_name = selected_track['name']
        artist_name = selected_track['artists'][0]['name']

        return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Now Playing</title>
                <style>
                    body {
                        font-family: 'Arial', sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        background-color: #f0f4f8;
                        margin: 0;
                    }
                    h1 {
                        color: #333;
                    }
                    h2 {
                        color: #555;
                    }
                    button {
                        margin-top: 20px;
                        padding: 10px 20px;
                        font-size: 16px;
                        color: white;
                        background-color: #007bff;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        transition: background-color 0.3s;
                    }
                    button:hover {
                        background-color: #0056b3;
                    }
                </style>
                <script>
                    function playSong() {
                        var iframe = document.getElementById('spotify-player');
                        iframe.src += '?autoplay=1'; // Add autoplay parameter
                    }
                </script>
            </head>
            <body onload="playSong()">
                <h1>Now Playing: {{ track_name }}</h1>
                <h2>Artist: {{ artist_name }}</h2>
                <h3>Detected Emotion: {{ emotion }}</h3>
                <iframe id="spotify-player" src="https://open.spotify.com/embed/track/{{ track_id }}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                <br>
                <button onclick="window.location.href='/capture'">Capture Another Emotion</button>
            </body>
            </html>
        ''', track_name=track_name, artist_name=artist_name, emotion=emotion, track_id=selected_track['id'])

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>No Music Found</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    background-color: #f0f4f8;
                    margin: 0;
                }
                h1 {
                    color: #333;
                }
                button {
                    padding: 10px 20px;
                    font-size: 16px;
                    color: white;
                    background-color: #007bff;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                button:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <h1>No Songs Found for Emotion: {{ emotion }}</h1>
            <button onclick="window.location.href='/'">Capture Another Emotion</button>
        </body>
        </html>
    ''', emotion=emotion)

if __name__ == '__main__':
    app.run(debug=True)
