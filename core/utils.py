import os
import subprocess
import re
import logging
import time
from constants import (MAX_LOG_FILES, LOG_DIR)

def setup_logging():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    monotonic_time = int(time.monotonic())
    log_file = os.path.join(LOG_DIR, f"debug_uptime_{monotonic_time}.log")

    # remove old logs if exceeding limit
    log_files = sorted(
        [f for f in os.listdir(LOG_DIR) if f.startswith("debug_uptime_")],
        key=lambda f: os.path.getmtime(os.path.join(LOG_DIR, f))
    )
    while len(log_files) >= MAX_LOG_FILES:
        oldest = log_files.pop(0)
        try:
            os.remove(os.path.join(LOG_DIR, oldest))
        except Exception as e:
            print(f"Failed to delete old log {oldest}: {e}")

    # configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def run_cmd(cmd):
    logging.debug(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        logging.debug(f"Command output: {result.stdout.strip()}")
        if result.stderr:
            logging.debug(f"Command error output: {result.stderr.strip()}")
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Exception while running command {' '.join(cmd)}: {e}")
        return ""


def clean_files(*files):
    for f in files:
        try:
            if os.path.exists(f):
                os.remove(f)
                logging.debug(f"Removed file: {f}")
        except Exception as e:
            logging.warning(f"Failed to remove {f}: {e}")


def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def is_ssh_connected():
    try:
        output = subprocess.check_output(["who"]).decode()
        return any("pts/" in line and "(" in line for line in output.splitlines())
    except Exception:
        return False

def shutdown_device():
    try:
        subprocess.call(["sudo", "shutdown", "now"])
    except Exception as e:
        logging.error(f"Shutdown failed: {e}")

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

def wait_for_time_sync(timeout=30):
    logging.info("Waiting for NTP time sync...")
    for _ in range(timeout):
        try:
            current_year = int(time.strftime("%Y"))
            if current_year >= 2024:
                now = time.strftime("%Y-%m-%d %H:%M:%S")
                logging.info(f"System time appears to be synced: {now}")
                return
        except Exception:
            pass
        time.sleep(1)
    logging.warning("System time may not be synced after waiting.")
