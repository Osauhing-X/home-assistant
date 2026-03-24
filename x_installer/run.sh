#!/usr/bin/env bash
echo "=== X Plugins Installer Add-on starting ==="
while true; do
    date +"Plugin check started at: %Y-%m-%d %H:%M:%S"
    python3 /app/installer.py
    sleep 3600  # 1h
done