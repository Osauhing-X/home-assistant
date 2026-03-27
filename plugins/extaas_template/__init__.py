from homeassistant.core import HomeAssistant
from .coordinator import ExtaasCoordinator
from .helpers.devices import create_device_with_heartbeat, create_dynamic_entities, update_parent_child_devices
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass, entry):
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator, "child_devices": {}}

    # Loome parent + child + heartbeat
    parent, child = await create_device_with_heartbeat(
        hass, entry, entry.data["host"], entry.data["port"],
        entry.data.get("hostname", entry.data["host"]),
        entry.data.get("name", f"Service {entry.data['port']}")
    )

    # Loome dünaamilised entity-d
    await create_dynamic_entities(hass, entry, entry.data["host"], entry.data["port"], child, coordinator.node_data)

    # Forward platvormid
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch"])

    # Options listener
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True

async def update_listener(hass, entry):
    """Värskendab device ja entity nime/options."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    host = entry.options.get("host", entry.data["host"])
    port = entry.options.get("port", entry.data["port"])
    hostname = entry.options.get("hostname", entry.data.get("hostname", host))
    node_name = entry.options.get("name", entry.data["name"])

    await update_parent_child_devices(hass, entry, host, port, hostname, node_name)