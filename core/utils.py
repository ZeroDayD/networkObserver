import os
import subprocess
import re
import logging

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
