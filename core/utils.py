import os
import subprocess
import re
import logging
from datetime import datetime
from pathlib import Path

def setup_logging():
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = logs_dir / f"debug_{timestamp}.log"

    # Configure logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Remove old logs (keep only the last 5)
    log_files = sorted(logs_dir.glob("debug_*.log"), key=os.path.getmtime, reverse=True)
    for old_file in log_files[5:]:
        try:
            old_file.unlink()
        except Exception as e:
            logging.warning(f"Could not delete old log file {old_file}: {e}")


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
