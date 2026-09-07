#!/usr/bin/with-contenv bashio
set -euo pipefail

mkdir -p /data/repositories /data/logs /data/runtime

# Older Huawei sticks can initially present themselves as a CD-ROM. The E392u-12
# uses 12d1:1505 in that mode and exposes its modem interfaces as 12d1:1506.
for USB_DEVICE in /sys/bus/usb/devices/*; do
  [ -r "$USB_DEVICE/idVendor" ] && [ -r "$USB_DEVICE/idProduct" ] || continue
  USB_VENDOR="$(cat "$USB_DEVICE/idVendor")"
  USB_PRODUCT="$(cat "$USB_DEVICE/idProduct")"
  if [ "$USB_VENDOR:$USB_PRODUCT" = "12d1:1505" ]; then
    echo "[X Platform] Switching Huawei E392 from storage mode to modem mode"
    usb_modeswitch -v 0x12d1 -p 0x1505 -V 0x12d1 -P 0x1506 \
      -M '55534243123456780000000000000011062000000100000000000000000000' || true
  fi
done

export PORT="$(bashio::config 'port')"

echo "[X Platform] Starting plugin manager"
node /app/manager.mjs &
MANAGER_PID=$!

echo "[X Platform] Starting Home Assistant bridge"
node /app/ha-bridge.mjs &
BRIDGE_PID=$!

cleanup() {
  kill "$MANAGER_PID" 2>/dev/null || true
  kill "$BRIDGE_PID" 2>/dev/null || true
}
trap cleanup EXIT TERM INT

echo "[X Platform] Starting console on port ${PORT}"
exec node /app/build/index.js
