import os
from deepgram import Deepgram
import asyncio, json
import hashlib
from pathlib import Path
import os

def hash256(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

# Your Deepgram API Key
DEEPGRAM_API_KEY = os.environ["DEEPGRAM_API_KEY"]

async def speech_recognition(filepath):
  # Initialize the Deepgram SDK
  dg_client = Deepgram(DEEPGRAM_API_KEY)
  # Open the audio file
  with open(filepath, 'rb') as audio:
    # Replace mimetype as appropriate
    source = {'buffer': audio, 'mimetype': 'audio/wav'}
    response = await dg_client.transcription.prerecorded(source, {'punctuate': True})
    return response

def transcribe(url, filepath=None):
    tmp_dir = Path("tmp_speech")
    tmp_dir.mkdir(exist_ok=True)
    if filepath is None:
        filepath = tmp_dir / (hash256(url) + ".m4a")

    if not filepath.is_file():
        os.system(f"yt-dlp -f wa -x --audio-format m4a --max-filesize 3m -o {filepath} {url}")

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(speech_recognition(filepath))
