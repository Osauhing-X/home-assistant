#!/usr/bin/env bash
set -e

echo "=== X Plugins Installer Add-on starting ==="

# Käivituse kuupäev ja kellaaeg
DATE=$(date '+%Y-%m-%d %H:%M:%S')
echo "Plugin check started at: $DATE"

# Käivita NodeJS/Python script
python3 /app/installer.py