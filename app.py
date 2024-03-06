import asyncio
import websockets
from flask import Flask, render_template
import pyaudio
import wave
import threading
import time

app = Flask(__name__)

# Global variables for audio streaming
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
audio_data_queue = asyncio.Queue()

# Function to stream audio data
def stream_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        data = stream.read(CHUNK)
        audio_data_queue.put_nowait(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

# WebSocket endpoint
@app.websocket('/audio')
async def audio(websocket):
    try:
        while True:
            # Get audio data from the queue
            audio_data = await audio_data_queue.get()
            await websocket.send(audio_data)
    except websockets.exceptions.ConnectionClosedOK:
        print("WebSocket connection closed")

# Route to serve the frontend HTML file
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Start the audio streaming thread
    audio_thread = threading.Thread(target=stream_audio)
    audio_thread.daemon = True
    audio_thread.start()

    # Run the Flask application
    app.run(debug=True)
