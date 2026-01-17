#!/usr/bin/with-contenv bashio
set -e

echo "Starting ESP32 BLE Presence Addon..."

export MQTT_BROKER="$(bashio::config 'mqtt_broker')"
export ZIGBEE_TOPIC="$(bashio::config 'zigbee_topic')"
export SCAN_INTERVAL_SEC="$(bashio::config 'scan_interval_sec')"
export RSSI_THRESHOLD="$(bashio::config 'rssi_threshold')"

exec python3 /app.py
