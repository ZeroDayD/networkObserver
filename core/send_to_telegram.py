import logging
import requests
from constants import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Missing 'telegram_token' or 'chat_id' in config.json")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
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
