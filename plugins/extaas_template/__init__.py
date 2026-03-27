from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from .coordinator import ExtaasCoordinator
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass, entry):
    coordinator = ExtaasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "node_full": {}
    }

    await async_update_device(hass, entry)

    # 🔥 options listener
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch"])

    return True


async def async_unload_entry(hass, entry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


# ✅ device registry sync
async def async_update_device(hass, entry):
    registry = dr.async_get(hass)

    registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(entry.domain, f"{entry.data['host']}:{entry.data['port']}")},
        name=entry.data["name"],
        manufacturer="Extaas",
        model="Node Service",
    )


# ✅ options live update
async def update_listener(hass, entry):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    coordinator.host = entry.options.get("host", entry.data["host"])
    coordinator.port = entry.options.get("port", entry.data["port"])

    await coordinator.async_request_refresh()