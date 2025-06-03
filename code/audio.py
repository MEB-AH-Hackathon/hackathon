import os
import requests
from dotenv import load_dotenv

# Load API token from .env
load_dotenv()
API_TOKEN = os.getenv("AUDIO_API_TOKEN")

# Paths & endpoints
upload_url = "https://groovy.audioshake.ai/upload/"
align_transcribe_url = "https://groovy.audioshake.ai/lyrics/align-transcribe"
file_path = "../data/happy-birthday-254480.mp3"

# Headers (Content-Type handled by requests for file upload)
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

def upload_file(path):
    with open(path, "rb") as f:
        files = {"file": f}
        print(f"Uploading {path}...")
        res = requests.post(upload_url, headers=headers, files=files)
        res.raise_for_status()
        return res.json()

def request_transcription(asset_id):
    headers_json = headers.copy()
    headers_json["Content-Type"] = "application/json"
    payload = {"assetId": asset_id}
    print(f"Requesting transcription for asset ID: {asset_id}")
    res = requests.post(align_transcribe_url, headers=headers_json, json=payload)
    res.raise_for_status()
    return res.json()

if __name__ == "__main__":
    try:
        # Step 1: Upload
        upload_result = upload_file(file_path)
        asset_id = upload_result["id"]
        print("Upload successful:", upload_result)

        # Step 2: Transcription + Alignment
        transcription_result = request_transcription(asset_id)
        print("Transcription request submitted:", transcription_result)

    except Exception as e:
        print("Error:", e)
