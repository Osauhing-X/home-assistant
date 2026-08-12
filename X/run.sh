#!/usr/bin/with-contenv bashio
set -euo pipefail

mkdir -p /data/repositories /data/logs /data/runtime

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
