import time
import logging
from utils import run_cmd
from constants import ATTACK_INTERFACE


def connect_to_wifi(essid, pin=None, psk=None):
    logging.info("Preparing Wi-Fi interface...")
    run_cmd(["sudo", "ip", "link", "set", ATTACK_INTERFACE, "down"])
    run_cmd(["sudo", "iw", ATTACK_INTERFACE, "set", "type", "managed"])
    run_cmd(["sudo", "ip", "link", "set", ATTACK_INTERFACE, "up"])
    logging.debug("Interface is now in managed mode.")

    logging.info("Triggering initial Wi-Fi rescan...")
    run_cmd(["nmcli", "device", "wifi", "rescan"])

    logging.info(f"Looking for SSID: {essid}")
    for attempt in range(15):
        scan_output = run_cmd([
            "nmcli", "-t", "-f", "SSID", "device", "wifi", "list",
            "ifname", ATTACK_INTERFACE
        ])
        logging.debug(f"Scan result (attempt {attempt + 1}): {scan_output}")
        if essid in scan_output:
            logging.info(f"SSID {essid} found.")
            break
        time.sleep(5)
    else:
        logging.warning(f"SSID {essid} was not found after multiple scans.")
        return False

    logging.info("Deleting old Wi-Fi connections with same SSID...")
    run_cmd(["nmcli", "connection", "delete", essid])
    run_cmd(["nmcli", "connection", "delete", f'"{essid}"'])
    run_cmd(["nmcli", "connection", "delete", f"'{essid}'"])

    password = pin or psk
    method = "PIN" if pin else "PSK"
    logging.info(f"Attempting to connect using {method}...")

    result = run_cmd([
        "nmcli", "device", "wifi", "connect", essid,
        "password", password,
        "ifname", ATTACK_INTERFACE
    ])
    logging.debug(f"nmcli connection result: {result}")

    if "Error:" in result or "failed" in result.lower():
        logging.error(f"Connection failed: {result}")
        return False

    time.sleep(5)
    ip_output = run_cmd(["ip", "addr", "show", ATTACK_INTERFACE])
    logging.debug(f"IP info: {ip_output}")
    if "inet " in ip_output:
        logging.info(f"Connected to {essid} successfully with IP.")
        return True
    else:
        logging.warning("Connection established, but no IP was assigned.")
        return False


def delete_all_wifi_connections():
    import subprocess
    import logging

    try:
        # Delete all saved Wi-Fi connections
        result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        deleted_any = False
        for line in result.stdout.strip().split("\n"):
            if ":wifi" in line:
                conn_name = line.split(":")[0]
                subprocess.run(["nmcli", "connection", "delete", conn_name], check=False)
                logging.info(f"Deleted saved Wi-Fi connection: {conn_name}")
                deleted_any = True

        if not deleted_any:
            logging.info("No saved Wi-Fi connections to delete.")

        # Delete all active Wi-Fi connections
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )

        for line in result.stdout.strip().split("\n"):
            if ":wifi:connected" in line:
                device = line.split(":")[0]
                subprocess.run(["nmcli", "device", "disconnect", device], check=False)
                logging.info(f"Disconnected Wi-Fi device: {device}")

    except Exception as e:
        logging.warning(f"Failed to clean/disconnect Wi-Fi connections: {e}")
