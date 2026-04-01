# X Ecosystem Documentation (X Plugins Installer + X Entities)

Developed by Osaühing X (Estonia Company)
Website: https://extaas.com

---

# 1. Overview

This system consists of:

### 1. X Plugins Installer (Addon)
- Installs & updates integrations from GitHub
- Runs automatically on interval
- Detects integrations via `"x": true`

### 2. X Entities (Integration)
- Receives data from Node.js or other services
- Creates dynamic entities inside Home Assistant
- Handles updates, storage, and communication

---

# 2. Architecture

Node App → REST API → X Entities → Home Assistant UI

- Node sends data → `/api/extaas_com`
- HA creates/updates entities dynamically
- User interacts → HA sends `/update` back to Node

---

# 3. X Plugins Installer (Addon)

## config.yaml
- repo: list of GitHub repos
- interval: update interval (seconds)

## Behavior
- Downloads repo ZIP
- Reads `/plugins`
- Validates `manifest.json`
- Copies new version → `new_version`
- Integration handles update itself

---

# 4. X Entities Integration

## Features
- Dynamic entities
- Zeroconf discovery
- Update entity
- Persistent storage
- Bidirectional communication

---

# 5. Node.js Demo (FULL)

Install:
npm install express bonjour node-fetch

Run example:

```js
import express from "express";
import bonjour from "bonjour";
import fetch from "node-fetch";

const app = express();
app.use(express.json());

const PORT = 3001;
const DOMAIN = "extaas_com";

let nodeData = {
  light: { name: "Light", value: false, type: "switch" },
  temp: { name: "Temp", value: 22, type: "sensor" },
  reboot: { name: "Reboot", value: false, type: "button" }
};

app.get("/heartbeat", (_, res) => res.send("OK"));

app.post("/update", (req, res) => {
  const updates = req.body;
  Object.keys(updates).forEach(k => {
    if (!nodeData[k]) return;
    nodeData[k].value = updates[k];
  });
  res.json({ ok: true });
});

app.listen(PORT);

let haUrl = null;

bonjour().find({ type: "home-assistant" }).on("up", s => {
  const ip = s.addresses.find(a => a.includes("."));
  if (ip) haUrl = `http://${ip}:${s.port}`;
});

async function send() {
  if (!haUrl) return;

  await fetch(`${haUrl}/api/${DOMAIN}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      host: "localhost",
      port: PORT,
      node_data: nodeData
    })
  });
}

setInterval(send, 5000);
```

---

# 6. Custom Integration Support (IMPORTANT)

If you want your integration to work with **x_installer**, you MUST follow this structure.

## 6.1 manifest.json

```json
{
  "x": true,
  "domain": "your_domain",
  "name": "Your Integration",
  "version": "1.0.0",
  "config_flow": true,
  "integration_type": "hub",
  "iot_class": "local_polling",
  "requirements": [],
  "dependencies": ["http"],
  "zeroconf": ["_extaas_com._tcp.local."]
}
```

### Required fields:
- `"x": true` → REQUIRED (otherwise installer ignores it)
- `"version"` → REQUIRED for updates
- `"integration_type": "hub"` → REQUIRED for update support

---

## 6.2 __init__.py (minimal)

```python
async def async_setup_entry(hass, entry):
    return True
```

---

## 6.3 update.py (REQUIRED for updates)

```python
from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from pathlib import Path
import shutil, asyncio

class CustomUpdateEntity(UpdateEntity):

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._attr_supported_features = UpdateEntityFeature.INSTALL

    async def async_install(self, version, backup, **kwargs):
        base = Path(__file__).parent
        new = base / "new_version"

        if not new.exists():
            return

        def do_update():
            tmp = base.parent / "tmp"
            old = base.parent / "old"

            shutil.move(new, tmp)
            shutil.move(base, old)
            shutil.move(tmp, base)
            shutil.rmtree(old)

        await self.hass.async_add_executor_job(do_update)
        await asyncio.sleep(1)

        await self.hass.services.async_call("homeassistant", "restart")
```

---

# 7. Entity Types

| Type   | Description |
|--------|------------|
| sensor | Read-only value |
| switch | ON/OFF |
| button | Action trigger |

---

# 8. Limits & Performance

- Max 500 entities per node
- Too many entities = slow HA
- Use batching wisely

---

# 9. Best Practices

- Always validate JSON
- Handle network failures
- Keep heartbeat stable
- Use proper naming for entities

---

# 10. Troubleshooting

Problem → Cause

- Node not visible → Zeroconf blocked
- No updates → missing `"x": true`
- Entities missing → bad payload
- Update fails → no `new_version` folder

---

# 11. Summary

- x_installer = installs & updates integrations
- x_entities = runtime bridge for devices
- Node apps = data providers

---

All components are developed and maintained by **Osaühing X (Estonia Company)**.
