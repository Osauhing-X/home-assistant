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

    # options listener
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch"])

    return True

async def async_unload_entry(hass, entry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


async def async_update_device(hass, entry):
    """Loob ainult child device (service/port) – host = grupi tasand"""
    registry = dr.async_get(hass)

    host = entry.data["host"]
    port = entry.data["port"]
    service_name = entry.data.get("name")

    # 🔥 CHILD device (service/port)
    registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(entry.domain, f"{host}:{port}")},
        name=service_name,
        manufacturer="Extaas",
        model="Service",
        via_device=None  # parent = host grupina ainult UI-s
    )


async def update_listener(hass, entry):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    coordinator.host = entry.options.get("host", entry.data["host"])
    coordinator.port = entry.options.get("port", entry.data["port"])
    coordinator.node_name = entry.options.get("name", entry.data["name"])

    registry = dr.async_get(hass)

    host = coordinator.host
    port = coordinator.port

    # update GROUP
    group = registry.async_get_device(identifiers={(entry.domain, host)})
    if group:
        registry.async_update_device(
            group.id,
            name=entry.options.get("hostname", entry.data.get("hostname"))
        )

    # update CHILD
    device = registry.async_get_device(identifiers={(entry.domain, f"{host}:{port}")})
    if device:
        registry.async_update_device(
            device.id,
            name=coordinator.node_name
        )

    await coordinator.async_request_refresh()