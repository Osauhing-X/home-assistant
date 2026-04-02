# DOCS.md

## Developed by Osaühing X (Estonia Company)

---

# Table of Contents
1. [X Plugins Installer](#x-plugins-installer)
   - Overview
   - Installation
   - Plugin Structure
   - Manifest Example
   - init.py Example
   - update.py Example
   - Demo Plugin
   - Common Pitfalls & Fixes

2. [X Entities](#x-entities)
   - Overview
   - Integration with Node.js
   - Entity Structure
   - Demo Node.js Application
   - Communication Flow
   - Common Issues & Fixes

3. [Best Practices & Notes](#best-practices--notes)

---

## X Plugins Installer

### Overview
`X Plugins Installer` is a system for managing Home Assistant plugins, handling installation, updates, and removal of integrations. It supports both default integrations provided by Osaühing X and user-created public GitHub integrations.

### Installation
1. Download the installer package.
2. Place it in your Home Assistant addons folder.
3. Restart Home Assistant.

### Plugin Structure
Each plugin must have the following structure:
```
plugin_name/
├── manifest.json
├── __init__.py
├── update.py
└── README.md
```

### Manifest Example
```json
{
  "x": true,
  "domain": "extaas_com",
  "name": "X Entities",
  "version": "0.0.1",
  "changelog": [
    "Demo example",
    "Few Improvmence" ],
  "config_flow": true,
  "iot_class": "local_polling",
  "requirements": ["aiohttp"],
  "dependencies": ["http", "zeroconf"],
  "zeroconf": ["_extaas_com._tcp.local."],
  "integration_type": "hub"
}
```

### init.py Example
```python
print("Initializing Demo Plugin")

def start():
    print("Plugin started")

if __name__ == '__main__':
    start()
```

### update.py Example
```python
import json

print("Running update script")

def update():
    print("Checking for updates...")
    # Example logic: fetch new manifest, compare versions
    # If new version found, download and replace files

if __name__ == '__main__':
    update()
```

### Demo Plugin
Copy-paste this structure into a folder and run `init.py` to test:
```
plugin_demo/
├── manifest.json
├── init.py
└── update.py
```
- `init.py` prints "Plugin started"
- `update.py` prints "Running update script"

### Common Pitfalls & Fixes
- **Manifest not found** → Ensure `manifest.json` is in plugin root.
- **Version mismatch on update** → Verify semantic versioning.
- **Python errors** → Ensure Python 3.10+ is used.

---

## X Entities

### Overview
`X Entities` provides a way for Node.js applications to interact with Home Assistant entities. It supports real-time updates, zeroconf discovery, and automatic integration with `X Plugins Installer` managed plugins.

### Integration with Node.js
Dependencies:
```bash
npm install bonjour axios
```

Node.js app example that detects `X Entities` services and interacts:
```javascript
const Bonjour = require('bonjour');
const axios = require('axios');

const bonjour = new Bonjour();

// Discover services
bonjour.find({ type: 'x_entity' }, (service) => {
    console.log('Discovered entity:', service.name);
    // Fetch current state
    axios.get(`http://${service.referer.address}:${service.port}/state`)
         .then(res => console.log(res.data))
         .catch(err => console.error(err));
});
```

### Entity Structure
Each entity must expose a REST API with the following endpoints:
- `GET /state` → returns JSON of current entity state
- `POST /update` → accepts JSON to update entity state

Example entity JSON:
```json
{
  "id": "light.kitchen",
  "type": "light",
  "state": "off",
  "brightness": 0
}
```

### Demo Node.js Application
1. Create `entity_server.js`:
```javascript
const express = require('express');
const app = express();
app.use(express.json());

let entityState = { state: 'off', brightness: 0 };

app.get('/state', (req, res) => {
    res.json(entityState);
});

app.post('/update', (req, res) => {
    entityState = { ...entityState, ...req.body };
    res.json(entityState);
});

app.listen(3000, () => console.log('Entity server running on port 3000'));
```
2. Run `node entity_server.js` and test with `curl` or your browser.

### Communication Flow
1. `X Plugins Installer` installs a plugin.
2. Node.js app discovers entities via zeroconf.
3. Node.js app fetches and updates entity states.
4. Home Assistant reflects updates in real time.

### Common Issues & Fixes
- **Zeroconf discovery fails** → Ensure multicast is allowed on your network.
- **Entity state not updating** → Check POST JSON format and headers.
- **Plugin not managed by installer** → Ensure manifest entry is correct.

---

## Best Practices & Notes
- Always maintain semantic versioning for plugins.
- Keep entity API responses consistent.
- Test plugins in a demo environment before production.
- Document every endpoint and manifest key.
- Monitor update scripts for errors and logs.
- Avoid using synchronous blocking calls in Node.js entities.
- Use `console.log` or logging libraries to trace flow.
