import time
import logging
import subprocess
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
        scan_output = run_cmd([
            "nmcli", "-t", "-f", "SSID", "dev", "wifi", "list",
            "ifname", ATTACK_INTERFACE
        ])
        logging.debug(f"Scan output (attempt {attempt + 1}): {scan_output}")
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

    password = pin or psk
    method = "PIN" if pin else "PSK"
    logging.info(f"Connecting to {essid} with {method}...")

    result = run_cmd([
        "nmcli", "dev", "wifi", "connect", essid,
        "password", password,
        "ifname", ATTACK_INTERFACE
    ])
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


def delete_all_wifi_connections():
    try:
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
                subprocess.run(["nmcli", "connection", "delete", "id", conn_name], check=False)
                logging.info(f"Deleted Wi-Fi connection: {conn_name}")
                deleted_any = True

        if not deleted_any:
            logging.info("No Wi-Fi connections to delete.")

    except Exception as e:
        logging.warning(f"Failed to clean Wi-Fi connections: {e}")
