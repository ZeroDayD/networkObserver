from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

# Config values
TELEGRAM_TOKEN = config["telegram_token"]
TELEGRAM_CHAT_ID = config["chat_id"]
STOP_ON_SUCCESS = config.get("stop_on_success", True)
SHUTDOWN_ON_COMPLETE = config.get("shutdown_on_complete", True)
ATTACK_INTERFACE = config.get("attack_interface", "wlan1")
MIN_SIGNAL_DBM = config.get("min_signal_dbm", -70)
WPS_TIMEOUT = config.get("wps_timeout_sec", 300)

# Hard-coded constants
TARGETS_FILE = BASE_DIR / "data" / "targets.json"
CRACKED_FILE = BASE_DIR / "data" / "cracked.json"
DEBUG_LOG = BASE_DIR / "logs" / "debug.log"
PCAP_FILE = BASE_DIR / "logs" / "reaver_output.pcap"
OUI_FILE = BASE_DIR / "data" / "oui_map.txt"
