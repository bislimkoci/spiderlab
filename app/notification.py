import requests
import os
from dotenv import load_dotenv

def send_detection_message_discord():
    load_dotenv()

    WEBHOOK_URL = os.getenv("DETECTION_WEBHOOK")

    data = {
        "content": "Person detected in Bises room"
    }

    response = requests.post(WEBHOOK_URL, json=data)

    if response.status_code == 204:
        print("Detection message sent")
    else:
        print("Error:", response.status_code, response.text)
