import os
import json
import requests
import logging

def send_message(message):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    
    try:
        with open(config_path) as f:
            config = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load config.json: {e}")
        return

    token = config.get("telegram_token")
    chat_id = config.get("chat_id")
    if not token or not chat_id:
        logging.error("Missing 'telegram_token' or 'chat_id' in config.json")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            logging.info("Message sent to Telegram.")
        else:
            logging.error(f"Failed to send message. HTTP {response.status_code}: {response.text}")
    except Exception as e:
        logging.exception(f"Exception while sending Telegram message: {e}")
