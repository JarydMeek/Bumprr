import requests
from config import get_config

def send_discord_notification(title, message):
    config = get_config()
    print(config)
    enabled = config.get('notifications', {}).get('discord', {}).get('enabled', False)
    webhook_url = config.get('notifications', {}).get('discord', {}).get('webhook_url', '')

    if not enabled:
        print("Discord notifications are disabled.")
        return

    if not webhook_url:
        print("Discord webhook URL not configured.")
        return

    payload = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": 5814783
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord notification: {e}")