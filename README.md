# Network Observer

A lightweight automated tool for wireless network reconnaissance and WPS-based attacks using [Wifite2](https://github.com/kimocoder/wifite2) on headless devices like Raspberry Pi Zero.

> ⚠️ **Educational Use Only**  
> This project is intended strictly for cybersecurity research, education, and authorized testing of networks you own or have explicit permission to audit. Any misuse is strongly discouraged and entirely your responsibility.

---

## Features

- Passive Wi-Fi scan for nearby access points
- Target filtering based on signal strength
- WPS PIN/PSK attacks using [Wifite2](https://github.com/kimocoder/wifite2) internal logic
- Automatic connection to compromised networks
- Telegram alert with credentials (PSK or WPS PIN)
- Auto-shutdown or persistent mode (depends on ssh connection)
- Systemd-compatible for headless deployment
- SSH session detection to prevent shutdown while connected

---

## Hardware Requirements

- Raspberry Pi Zero 2 W (or similar)
- External Wi-Fi adapter with monitor mode support (for `wlan1`)
- Power bank (for portable field use)
- Optional: small OLED/HDMI screen for local TUI (not implemented yet)

---

## Software Dependencies

Installed via `apt`:

```bash
sudo apt update
sudo apt install -y \
  aircrack-ng \
  wireless-tools \
  iw \
  tcpdump \
  curl \
  jq \
  arp-scan \
  network-manager \
  wifite \
  net-tools
```

## 🔧 Example systemd service

To automatically run `networkObserver` on boot via `systemd`, you can create a service like this:

```ini
[Unit]
Description=Auto-start networkObserver script on boot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/pi/networkObserver/core  # Change to your actual path
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=TERM=xterm
Environment=COLUMNS=80
Environment=LINES=24
ExecStartPre=/sbin/ip link set wlan1 down
ExecStartPre=/sbin/iw wlan1 set type monitor
ExecStartPre=/sbin/ip link set wlan1 up
ExecStart=/usr/bin/python3 /home/pi/networkObserver/core/main.py
StandardOutput=append:/home/pi/networkObserver/core/debug.log
StandardError=append:/home/pi/networkObserver/core/debug.log
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
