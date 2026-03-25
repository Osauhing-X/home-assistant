import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Setup without config.yaml support"""
    # Store all runtime info
    hass.data[DOMAIN] = {
        "connected": {},
        "value": {},
        "status": {},
        "last_seen": {},
        "sensors": {},
        "config": {}
    }
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup config entry"""
    store = hass.data[DOMAIN]

    # Salvesta config
    store["config"] = {
        "name": entry.data.get("name"),
        "host": entry.data.get("host"),
        "port": entry.data.get("port", 3000)
    }

    # Forward sensor platvorm
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Loo kohe heartbeat sensor, et integratsiooni kast püsiks
    from .sensor import XTemplateNodeSensor
    async def add_heartbeat():
        if "heartbeat" not in store["sensors"]:
            device_info = {
                "identifiers": {(DOMAIN, entry.entry_id)},
                "name": store["config"]["name"],
                "manufacturer": "Extaas",
                "model": "Node Client",
                "sw_version": f"Port {store['config']['port']}"
            }
            sensor = XTemplateNodeSensor(hass, "heartbeat", device_info)
            store["sensors"]["heartbeat"] = sensor
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
            )
    await add_heartbeat()

    return True