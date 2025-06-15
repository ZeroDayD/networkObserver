import os
import json
import requests
import logging

# Constants
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# Load config once
def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"[Telegram] Failed to load config.json: {e}")
        return {}

CONFIG = load_config()

def send_message(message: str) -> None:
    """
    Sends a message to a predefined Telegram chat using the bot token.
    Configuration must be in config.json with 'telegram_token' and 'chat_id'.
    """
    token = CONFIG.get("telegram_token")
    chat_id = CONFIG.get("chat_id")

    if not token or not chat_id:
        logging.error("[Telegram] Missing 'telegram_token' or 'chat_id' in config.json")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.ok:
            logging.info("[Telegram] Message sent successfully.")
        else:
            logging.error(f"[Telegram] Failed to send message. HTTP {response.status_code}: {response.text}")
    except Exception as e:
        logging.exception(f"[Telegram] Exception while sending message: {e}")
