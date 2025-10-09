import subprocess
import logging


def run_nmap_scan(interface_ip):
    try:
        logging.info(f"Running nmap scan on local network ({interface_ip}/24)...")
        result = subprocess.run(
            ["nmap", "-sV", "-O", "-T4", "-oN", "-", f"{interface_ip}/24"],
            capture_output=True, text=True, timeout=300
        )
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Failed to run nmap scan: {e}")
        return None

def get_wifi_ip(interface):
    try:
        ip_output = subprocess.check_output(["ip", "-4", "addr", "show", interface], text=True)
        for line in ip_output.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                return line.split()[1].split("/")[0]
    except Exception as e:
        logging.warning(f"Failed to get IP address of {interface}: {e}")
    return None

def clean_nmap_output(raw_output):
    lines = raw_output.splitlines()
    cleaned_lines = []
    inside_fingerprint = False

    for line in lines:
        if line.startswith("SF-Port"):
            inside_fingerprint = True
            continue
        if inside_fingerprint:
            if line.endswith('");'):
                inside_fingerprint = False
            continue
        if line.strip().startswith("# Nmap scan initiated") or line.strip().startswith("# Nmap done"):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()
