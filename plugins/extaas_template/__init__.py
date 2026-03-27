from homeassistant.core import HomeAssistant
from .coordinator import ExtaasCoordinator
from .devices import create_node_devices, update_node_devices
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    """Üldine setup, ei tee midagi."""
    return True

async def async_setup_entry(hass, entry):
    """Setup entry (coordinator + device + forward platforms)."""

    # Loo coordinator
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator, "child_device_id": None}

    # Loo parent + child + heartbeat + dünaamilised entity-d
    node_obj = await create_node_devices(
        hass, entry,
        {
            "host": entry.data["host"],
            "port": entry.data["port"],
            "hostname": entry.data.get("hostname", entry.data["host"]),
            "name": entry.data.get("name", f"Service {entry.data['port']}"),
            "dynamic_entities": coordinator.dynamic_entities
        }
    )

    hass.data[DOMAIN][entry.entry_id]["child_device_id"] = node_obj["child_device"].id

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
    node_name = entry.options.get("name", entry.data.get("name", coordinator.node_name))

    node_obj = {
        "host": host,
        "hostname": hostname,
        "service_name": node_name,
        "dynamic_entities": coordinator.dynamic_entities
    }

    await update_node_devices(hass, entry, {
        "parent_device": None,  # pole vajalik, uuendatakse registris
        "child_device": hass.data[DOMAIN][entry.entry_id]["child_device_id"]
    }, node_obj)