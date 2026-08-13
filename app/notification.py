import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("DETECTION_WEBHOOK") 

data = {
    "content": "Hello From Python"
}

response = requests.post(WEBHOOK_URL, json=data)

if response.status_code == 204:
    print("Message sent")
else:
    print("Error: ", response.status_code, response.text)