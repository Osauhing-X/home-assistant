# ESP32 BLE Presence Addon

Custom HA addon to manage ESP32 BLE presence sensors via Zigbee/MQTT.

## Features
- REST API `/devices`, `/heartbeat`, `/users`
- Add / update devices and users
- Frontend HTML + JS
- HA ingress support
- MQTT config push to ESP32 end device’ile

## Installation
1. Kopeeri kaust `ha-esp32-presence-addon` Home Assistant `addons/local` alla
2. Install addon Supervisor UI-st
3. Konfigureeri parameetrid (MQTT broker, Zigbee topic)
4. Start addon
5. Ava UI läbi HA paneli või ingressi
