import time
import logging
from utils import run_cmd
from constants import ATTACK_INTERFACE

def connect_to_wifi(essid, pin=None, psk=None):
    logging.info("Preparing interface...")
    run_cmd(["sudo", "ip", "link", "set", ATTACK_INTERFACE, "down"])
    run_cmd(["sudo", "iw", ATTACK_INTERFACE, "set", "type", "managed"])
    run_cmd(["sudo", "ip", "link", "set", ATTACK_INTERFACE, "up"])

    logging.debug("Interface set to managed mode and brought up.")

    logging.info(f"Waiting for {essid} to appear in scan...")
    for attempt in range(15):
        scan_output = run_cmd(["nmcli", "-t", "-f", "SSID", "dev", "wifi", "list", "ifname", ATTACK_INTERFACE])
        logging.debug(f"Scan output (attempt {attempt+1}): {scan_output}")
        if essid in scan_output:
            logging.info(f"{essid} found in scan.")
            break
        time.sleep(5)
    else:
        logging.warning(f"{essid} not visible after scan attempts.")
        return False

    logging.info("Cleaning up old connections...")
    run_cmd(["nmcli", "connection", "delete", essid])
    run_cmd(["bash", "-c", f"nmcli connection delete id \"{essid}\" || true"])
    run_cmd(["bash", "-c", f"nmcli connection delete id '{essid}' || true"])

    logging.info(f"Connecting to {essid} with {'PIN' if pin else 'PSK'}...")
    result = run_cmd(["nmcli", "dev", "wifi", "connect", essid, "password", pin or psk, "ifname", ATTACK_INTERFACE])
    logging.debug(f"nmcli output: {result}")

    if "Error:" in result or "failed" in result.lower():
        logging.error(f"nmcli reported connection error: {result}")
        return False

    time.sleep(5)
    ip_output = run_cmd(["ip", "addr", "show", ATTACK_INTERFACE])
    logging.debug(f"IP output: {ip_output}")
    if "inet " in ip_output:
        logging.info(f"Successfully connected to {essid}, IP assigned.")
        return True
    else:
        logging.warning(f"Connected to {essid} but no IP assigned.")
        return False
