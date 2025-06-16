import subprocess
import time
import json
import re
import logging
from utils import run_cmd, strip_ansi
from constants import TARGETS_FILE

MAX_SCAN_TIME = 75
POWER_COLUMN_INDEX = 4


def parse_wifite_line(line):
    line = strip_ansi(line.strip())
    if not line:
        return None

    logging.debug(f"[wifite] {line}")
    essid_match = re.search(r'\d+\s+(.+?)\s+\d+\s+WPA', line)
    if not essid_match:
        return None

    essid = essid_match.group(1).replace("*", "").strip()

    try:
        columns = line.split()
        power = int(columns[POWER_COLUMN_INDEX].replace('db', ''))
        return essid, power
    except Exception as e:
        logging.debug(f"Failed to extract power for {essid}: {e}")
        return None


def save_targets_to_file(targets):
    try:
        with open(TARGETS_FILE, "w") as f:
            json.dump(targets, f, indent=2)
        logging.info(f"{len(targets)} targets saved to {TARGETS_FILE}")
    except Exception as e:
        logging.error(f"Failed to save targets: {e}")


def scan_targets(interface):
    logging.info("Scanning for targets using wifite...")
    proc = subprocess.Popen(
        ["script", "-q", "-c", f"wifite --wps-only --ignore-locks -i {interface}", "/dev/null"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    targets = {}
    start_time = time.time()

    for line in iter(proc.stdout.readline, ""):
        if time.time() - start_time > MAX_SCAN_TIME:
            logging.warning(f"Scan timeout reached ({MAX_SCAN_TIME}s), terminating wifite.")
            proc.terminate()
            break

        parsed = parse_wifite_line(line)
        if parsed:
            essid, power = parsed
            if essid not in targets or targets[essid] < power:
                targets[essid] = power

    sorted_targets = sorted(targets.items(), key=lambda x: -x[1])
    save_targets_to_file(sorted_targets)
    return sorted_targets
