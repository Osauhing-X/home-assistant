#!/usr/bin/with-contenv bashio
set -e

echo "=== Debug: NodeJS Plugin Installer starting ==="

# Praegune töökaust
echo "Current working directory: $(pwd)"

# List root
echo "Listing root (/):"
ls -l /

# List /homeassistant, kui olemas
if [ -d "/homeassistant" ]; then
    echo "Listing /homeassistant:"
    ls -l /homeassistant
else
    echo "/homeassistant does not exist"
fi

# List /config, kui olemas
if [ -d "/config" ]; then
    echo "Listing /config:"
    ls -l /config
else
    echo "/config does not exist"
fi

# List /plugins, kui olemas
if [ -d "/plugins" ]; then
    echo "Listing /plugins:"
    ls -l /plugins
else
    echo "/plugins does not exist"
fi

echo "=== Debug log finished ==="

# Hoia konteiner PID 1-s käimas, et saaks logisid vaadata
tail -f /dev/null