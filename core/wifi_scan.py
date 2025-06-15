import subprocess
import time
import json
import re
import logging
from utils import run_cmd, strip_ansi
from constants import TARGETS_FILE

def scan_targets(interface):
    logging.info("Scanning for targets using wifite...")
    proc = subprocess.Popen(
        ["script", "-q", "-c", f"wifite --wps-only --ignore-locks -i {interface}", "/dev/null"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    targets = {}
    start_time = time.time()

    for line in iter(proc.stdout.readline, ""):
        if time.time() - start_time > 75:
            logging.warning("Scan timeout reached (75s), terminating wifite.")
            proc.terminate()
            break

        line = strip_ansi(line.strip())
        if not line:
            continue

        logging.debug(f"[wifite] {line}")

        essid_match = re.search(r'\d+\s+(.+?)\s+\d+\s+WPA', line)
        if essid_match:
            essid = essid_match.group(1).replace("*", "").strip()
            try:
                columns = line.split()
                power = int(columns[4].replace('db', ''))
                if essid not in targets or targets[essid] < power:
                    targets[essid] = power
            except Exception as e:
                logging.debug(f"Failed to extract power for {essid}: {e}")
                continue

    sorted_targets = sorted(targets.items(), key=lambda x: -x[1])
    try:
        with open(TARGETS_FILE, "w") as f:
            json.dump(sorted_targets, f, indent=2)
        logging.info(f"{len(sorted_targets)} targets saved to {TARGETS_FILE}")
    except Exception as e:
        logging.error(f"Failed to save targets: {e}")

    return sorted_targets
