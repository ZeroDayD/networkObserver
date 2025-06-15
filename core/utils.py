import os
import subprocess
import re
import logging
from constants import DEBUG_LOG


def setup_logging():
    os.makedirs(os.path.dirname(DEBUG_LOG), exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(DEBUG_LOG, mode="a"),
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
        output = subprocess.check_output(["ps", "-eo", "pid,ppid,user,args"]).decode()
        return "sshd:" in output or "pts/" in output
    except Exception as e:
        logging.warning(f"Failed to check SSH connection: {e}")
        return False


def shutdown_device():
    try:
        subprocess.call(["sudo", "shutdown", "now"])
    except Exception as e:
        logging.error(f"Shutdown failed: {e}")
