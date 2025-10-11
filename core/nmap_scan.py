import subprocess
import logging
import os
from constants import ENABLE_LLM_ANALYSIS


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

def get_llm_attack_insights(nmap_output):
    """Get LLM insights focused on attack vectors and tools using CLI"""
    if not ENABLE_LLM_ANALYSIS:
        return None
    
    try:
        import tempfile
        import os
        
        # Create focused prompt for attack vectors and tools
        prompt = f"""You are a penetration testing expert. Analyze this nmap scan and provide specific attack vectors and tool recommendations.Short, concise, and practical.

NMAP SCAN RESULTS:
{nmap_output[:3000]}

Please provide a focused analysis in markdown format with:

## 🎯 Attack Vectors
- List specific attack methods for discovered services
- Prioritize by likelihood of success

## 🛠️ Recommended Tools
- Specific tools/commands for each attack vector
- Include exact tool names and basic usage

## ⚡ Quick Wins
- Immediate vulnerabilities to exploit
- Low-hanging fruit

## 🔍 Further Investigation
- Additional scanning recommendations
- Services requiring deeper analysis

Keep responses practical and actionable for immediate use."""

        # Write prompt to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(prompt)
            temp_file_path = temp_file.name
        
        try:
            # Call LLM CLI with your syntax
            result = subprocess.run(
                ["llm", "-m", "gemini/gemini-2.0-flash"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logging.error(f"LLM CLI failed: {result.stderr}")
                return None
                
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
        
    except FileNotFoundError:
        logging.error("LLM CLI not found. Install with: pip install llm")
        return None
    except Exception as e:
        logging.error(f"LLM analysis failed: {e}")
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
