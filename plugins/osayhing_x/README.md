https://my.home-assistant.io/redirect/config_flow_start/?domain=extaas_template

--




http://home.local:8123/config/integrations/integration/extaas_template

https://developers.home-assistant.io/docs/network_discovery/

Node.js rakendus + mDNS auto-discovery + Zeroconf

# translations/en.json

# __init__.py
# api.py
# config_flow.py
# const.py
# coordinator.py
# devices_manager.py
# entities.py
# manifest.json
# registry.py
# sensor.py
# store.sh
# switch.py




Device Group (IP / hostname)
 └── Device (PORT / service)
      └── Entities (sensor / switch)








NT 1:
ENTRY (IP / hostname)
 └── DEVICE (PORT / service)
      ├── heartbeat (alati olemas)
      └── Entities (sensor / switch)

NT 2:
taavi-book-13 <- (10.10.1.99), (entry)
- Discord (10.10.1.99:3400) <- heartbeat sensor, muud sensorid ...
- Website (10.10.1.99:5003) <- heartbeat sensor, muud sensorid ...

asus_rog-7 (10.10.1.207)
- Discord (10.10.1.207:7300) <- heartbeat sensor, muud sensorid ...
- Website (10.10.1.207:6601) <- heartbeat sensor, muud sensorid ...

NT 3:
taavi-book-13 (10.10.1.99) (entry)
 ├── Discord (10.10.1.99:3400) (device)
 │    ├── heartbeat (entity)
 │    └── muud sensorid
 └── Website (5003)
      ├── heartbeat
      └── muud sensorid

asus_rog-7 (10.10.1.207)
 ├── X-API (7300)
 └── Discord_Bot_2 (6601)

---

Node → /api/extaas_template → HA (data)
HA → /heartbeat → Node (alive check)
HA → /update → Node (switch control)


 








ZEROCONF (data)

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


