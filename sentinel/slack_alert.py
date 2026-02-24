import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import os

SLACK_TOKEN = os.getenv("SLACK_TOKEN")
CHANNEL = "C0AAQ690FDK"

client = WebClient(token=SLACK_TOKEN)

LAST_ALERT_TIME = 0
ALERT_COOLDOWN = 10  # seconds

def send_alert(message):
    global LAST_ALERT_TIME

    current_time = time.time()

    # Throttle alerts
    if current_time - LAST_ALERT_TIME < ALERT_COOLDOWN:
        return  # skip alert silently

    try:
        client.chat_postMessage(
            channel=CHANNEL,
            text=f"🚨 *Sentinel Alert*\n{message}"
        )
        LAST_ALERT_TIME = current_time

    except SlackApiError as e:
        print("⚠️ Slack alert failed:", e.response["error"])
