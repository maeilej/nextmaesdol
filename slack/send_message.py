import requests
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_notification(title, details):
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{title}*\n{details}\n*시간:* `{time_stamp}`"
                }
            }
        ]
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=message)
    if response.status_code != 200:
        print(f"Error sending notification: {response.status_code}, {response.text}")