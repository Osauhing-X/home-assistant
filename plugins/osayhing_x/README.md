# Extaas Home Assistant Node Client

This guide explains how to build a Node.js application that integrates with the `extaas_com` Home Assistant integration. This solution allows for automatic discovery, dynamic entity management, and real-time synchronization.

---

## 🚀 Key Features

*   **Zero Configuration:** Uses Zeroconf (Bonjour) to automatically let Home Assistant find your node.
*   **Dynamic Entities:** Entities (Sensors, Switches, Buttons) are created in Home Assistant automatically based on your `nodeData` object.
*   **Bi-directional Sync:** 
    *   **Node to HA:** Updates are pushed to Home Assistant every 5 seconds or immediately on state change.
    *   **HA to Node:** Commands from the Home Assistant UI are sent to the Node's `/update` endpoint.
*   **Auto-Discovery of HA:** The node automatically searches the network for the Home Assistant instance to send data to the correct API endpoint.

---

## 🛠️ Implementation Guide

### 1. Requirements
Ensure you have a Node.js environment initialized:
```bash
npm init -y
npm install express bonjour node-fetch
```

### 2. The Universal Node Client (`app.js`)
This script handles the server, state management, and communication logic.

```javascript
import express from "express";
import bonjour from "bonjour";
import os from "os";
import fetch from "node-fetch";

// --- CONFIGURATION ---
const PORT = 3001;
const HOSTNAME = os.hostname();
const SERVICE_NAME = "SmartNode-01"; // Name displayed during discovery
const DOMAIN = "extaas_com";         // Must match the integration domain

// --- UTILITY: GET LOCAL IP ---
function getLocalIp() { let fb;
  for (const [n, i] of Object.entries(os.networkInterfaces()))
    for (const a of i)
       // check only IPv4 and skip internal/virtual interfaces
      if (a.family==="IPv4"&&!a.internal&&!/^(lo|docker|veth|br-|hassio|vmnet|vboxnet)/i.test(n))
        // return immediately if interface looks like a physical NIC (en/eth/wlan/wl), otherwise store as fallback
        return /^(en|eth|wlan|wl)/i.test(n)?a.address:(fb??a.address);
  return fb||"127.0.0.1"; }

const HOST_IP = getLocalIp();

// --- EXPRESS SERVER SETUP ---
const app = express();
app.use(express.json());

// --- INTERNAL STATE (NODE DATA) ---
// Define your entities here. The integration will create them in HA automatically.
let nodeData = {
  power_btn: {
    name: "System Restart",
    value: false,
    type: "button",
    icon: "mdi:power-cycle",
    device: "Main Controller"
  },
  status_led: {
    name: "Status LED",
    value: false,
    type: "switch",
    icon: "mdi:led-on",
    device: "Main Controller"
  },
  temperature: {
    name: "Environment Temp",
    value: 22.5,
    type: "sensor",
    icon: "mdi:thermometer",
    device_class: "temperature",
    unit: "°C",
    state_class: "measurement",
    device: "Sensor Hub",
  }
};

// --- HEARTBEAT ENDPOINT ---
// Home Assistant checks this to verify the node is "Online"
app.get("/heartbeat", (req, res) => {
  res.status(200).send("OK");
});

// --- UPDATE ENDPOINT (RECEIVING DATA FROM HA) ---
// Triggered when a user interacts with an entity in Home Assistant
app.post("/update", async (req, res) => {
  const updates = req.body;

  for (const key of Object.keys(updates)) {
    if (!nodeData[key]) continue;

    if (nodeData[key].type === "button") {
      console.log(`Action: Button ${key} pressed`);
      handleButtonAction(key);
    } else {
      console.log(`Action: ${key} updated to ${updates[key]}`);
      nodeData[key].value = updates[key];
    }
  }

  // Synchronize state back to HA immediately
  await sendDataToHA();
  res.json({ ok: true });
});

// --- LOGIC FOR BUTTON ENTITIES ---
function handleButtonAction(name) {
  if (name === "power_btn") {
    console.log("Restarting services...");
    // Example: Logic to restart hardware or software
  }
}

// --- START EXPRESS SERVER ---
app.listen(PORT, () => {
  console.log(`${HOSTNAME} is active at http://${HOST_IP}:${PORT}`);
});

// --- ZEROCONF BROADCASTING ---
// Publishes this node to the network for HA to discover

const bonjourService = bonjour();
if(HOST_IP && PORT){
  bonjourService.publish({
    host: HOST_IP,
    name: SERVICE_NAME,
    port: PORT,
    type: DOMAIN, 
    txt: { "data": JSON.stringify({
        integration: DOMAIN,
        hostname: HOSTNAME,
        service_name: SERVICE_NAME,
        model: "Generic Node Client" }) }
}) }

// --- DYNAMIC HA DISCOVERY ---
// Searches for Home Assistant in the network to obtain the API URL
let haUrl = null;
const browser = bonjourService.find({ type: "home-assistant" });

browser.on("up", (service) => {
  const ipv4 = service.addresses.find(a => a.includes("."));
  if (!ipv4) return;

  haUrl = `http://${ipv4}:${service.port}`;
  console.log("Discovered Home Assistant at:", haUrl);
});

// --- DATA SYNC TO HOME ASSISTANT ---
// Sends the nodeData object to the integration's API
async function sendDataToHA() {
  if (!haUrl) return;

  try {
    const response = await fetch(`${haUrl}/api/${DOMAIN}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        host: HOST_IP,
        port: PORT,
        node_data: nodeData
      })
    });
    
    if (response.ok) {
      console.log("Data synced successfully");
    }
  } catch (err) {
    console.log("Synchronization failed:", err.message);
  }
}

// --- AUTOMATIC UPDATES ---
// Regularly push state to ensure HA reflects current values
setInterval(sendDataToHA, 5000);

// --- EXAMPLE: SIMULATED SENSOR CHANGES ---
// Simulate a temperature change every 30 seconds
setInterval(() => {
  const variation = (Math.random() - 0.5);
  nodeData.temperature.value = parseFloat((nodeData.temperature.value + variation).toFixed(1));
  console.log("Sensor Update:", nodeData.temperature.value);
  sendDataToHA();
}, 30000);
```

---

## ⚙️ How it Works

1.  **Announcement:** The node uses Bonjour to say "I am an `extaas_com` device" at `192.168.x.x:3001`.
2.  **Registration:** Home Assistant's config flow sees this announcement and creates a Hub entry.
3.  **Discovery:** The node finds Home Assistant's own Bonjour broadcast to know where the `/api/extaas_com` endpoint is.
4.  **Handshake:** The node sends its `nodeData`. Home Assistant creates a sensor for `temperature`, a switch for `status_led`, and a button for `power_btn`.
5.  **Control:** If you flip the switch in HA, HA sends a POST to your node's `/update` route. Your code updates its internal state, and everyone stays in sync.

---

## Sensor Reference Table

### Sensor Types

| device_class            | unit_of_measurement     | state_class         | description             |
|-------------------------|-------------------------|---------------------|-------------------------|
| battery                 | %                       | measurement         | Battery level           |
| temperature             | °C, °F                  | measurement         | Temperature sensor      |
| humidity                | %                       | measurement         | Relative humidity       |
| power                   | W, kW                   | measurement         | Instantaneous power     |
| energy                  | Wh, kWh                 | total_increasing    | Energy usage            |
| voltage                 | V                       | measurement         | Electric voltage        |
| current                 | A                       | measurement         | Electric current        |
| signal_strength         | dBm                     | measurement         | WiFi or signal strength |
| timestamp               | ISO 8601 datetime       | none                | Date/time sensor        |
| pressure                | hPa, mbar               | measurement         | Air or fluid pressure   |
| power_factor            | %                       | measurement         | Electric power factor   |
| apparent_power          | VA                      | measurement         | Apparent power          |
| reactive_power          | VAR                     | measurement         | Reactive power          |
| energy_kva              | kVAh                    | total_increasing    | Energy in kVAh          |
| frequency               | Hz                      | measurement         | Electric frequency      |
| gas                     | ppm                     | measurement         | General gas sensor      |
| ozone                   | ppm, µg/m³              | measurement         | Ozone concentration     |
| nitrogen_dioxide        | µg/m³                   | measurement         | NO₂ concentration       |
| sulphur_dioxide         | µg/m³                   | measurement         | SO₂ concentration       |
| carbon_monoxide         | ppm                     | measurement         | CO concentration        |
| carbon_dioxide          | ppm                     | measurement         | CO₂ concentration       |
| pm1                     | µg/m³                   | measurement         | Particulate matter 1    |
| pm2_5                   | µg/m³                   | measurement         | Particulate matter 2.5  |
| pm10                    | µg/m³                   | measurement         | Particulate matter 10   |
| moisture                | %                       | measurement         | Moisture content        |
| illuminance             | lx                      | measurement         | Light intensity         |
| distance                | m                       | measurement         | Distance sensor         |
| sound                   | dB                      | measurement         | Sound level             |
| vibration               | m/s²                    | measurement         | Vibration sensor        |
| timestamp               | ISO 8601                | none                | Date/time sensor        |


---

### State Class Summary

measurement, total, total_increasing

---

### Notes

* device_class and unit must match correctly
* energy should use total_increasing
* measurement is used for real-time values
* total_increasing must never decrease
* timestamp does not use state_class


## 📌 Overview

Node → /api/extaas_template → HA (data)
HA → /heartbeat → Node (alive check)
HA → /update → Node (switch control)


ZEROCONF (data)
```
  ┌──ᐊ init.py
  │
  │
  ├─ᐅ 1. async_setup_entry
  │       // Receives entry data: host, port, service_name, node_name
  │       // Initializes runtime storage: hass.data[DOMAIN][entry.entry_id]
  │       // Sets up shared aiohttp session (closed on homeassistant_stop)
  │       // Creates ExtaasCoordinator
  │       // Forwards platforms: sensor, switch, button, update
  │       // Runtime holds coordinator and entity states
  │
  ├─ᐅ 2. hass.data
  │       // Stores:
  │       //  - coordinator → manages heartbeat and todo queue
  │       //  - entities → entry sensors, switches, buttons
  │       // Note: runtime data disappears on restart; entry persists in config entries
  │
  └─ᐅ config_flow.py (creating entry)
        │
        │
  ┌─────┘
  ├─ᐅ 1. async_step_zeroconf
  │       // Decode zeroconf TXT properties (bytes → str)
  │       // Set hostname = props["node_name"] || discovery_info.hostname
  │       // Set service_name = props["service_name"] || discovery_info.name
  │       // Temporarily save self._data = {hostname, service_name, host, port}
  │       // Duplicate check (IP + port)
  │       // Set unique_id and abort if entry already exists
  │       // Prepare UI title: title_placeholders["name"] = hostname - service_name
  │
  ├─ᐅ 2. async_step_confirm
  │       // Displays confirmation form to the user
  │       // If user_input exists → update self._data
  │       // Calls async_create_entry
  │
  ├─ᐅ 3. async_create_entry
  │       // Creates persistent config entry in Home Assistant:
  │       //  - title = self._data["service_name"]
  │       //  - data = self._data
  │       // Entry data is stored in `.storage/core.config_entries`
  │       // Entry triggers async_setup_entry
  │
  └─ᐅ entities.py (device and entity creation)
        │
        │
  ┌─────┘
  ├─ᐅ 1. BaseEntity
  │       // All Extaas entities inherit from BaseEntity
  │       // self.entry → access to entry.data
  │       // self.data → individual entity value from runtime hass.data
  │       // device_info defines entity’s device grouping:
  │       //    - if entity has "device" → grouped
  │       //    - if missing → use entry.data["friendly_name"]
  │
  └─ᐅ 2. ExtaasSensor / ExtaasSwitch / ExtaasButton
          // Inherits from BaseEntity
          // state/is_on reads self.data["value"]
          // Switch/button sends update to node server via `_send()`
          // Live updates handled by async_dispatcher_connect(SIGNAL_UPDATE)
```

