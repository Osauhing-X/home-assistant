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

    # Loome device group ja child device'id
    await async_update_device(hass, entry)

    # Options listener
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # Forward sensorid ja switchid platvormidele
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch"])

    return True

async def async_unload_entry(hass, entry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

async def async_update_device(hass, entry):
    """Loob hosti/device group (IP) ja child device'id (portid/teenused)."""
    registry = dr.async_get(hass)

    host = entry.data["host"]
    port = entry.data["port"]
    hostname = entry.data.get("hostname") or host
    service_name = entry.data.get("name") or f"Service {port}"

    # --- PARENT DEVICE (GROUP) ---
    parent_device = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(entry.domain, host)},
        name=hostname,  # hosti nimi
        manufacturer="Extaas",
        model="Host",
        sw_version=None
    )

    # --- CHILD DEVICE (SERVICE / PORT) ---
    registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(entry.domain, f"{host}:{port}")},
        name=service_name,
        manufacturer="Extaas",
        model="Service",
        via_device=(entry.domain, host)  # seostatakse parent device'iga
    )

async def update_listener(hass, entry):
    """Värskendab hosti ja child device'i nime, kui options muutuvad."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    coordinator.host = entry.options.get("host", entry.data["host"])
    coordinator.port = entry.options.get("port", entry.data["port"])
    coordinator.node_name = entry.options.get("name", entry.data["name"])
    coordinator.hostname = entry.options.get("hostname", entry.data.get("hostname", coordinator.host))

    registry = dr.async_get(hass)

    host = coordinator.host
    port = coordinator.port

    # Update GROUP
    group = registry.async_get_device(identifiers={(entry.domain, host)})
    if group:
        registry.async_update_device(
            group.id,
            name=coordinator.hostname
        )

    # Update CHILD
    device = registry.async_get_device(identifiers={(entry.domain, f"{host}:{port}")})
    if device:
        registry.async_update_device(
            device.id,
            name=coordinator.node_name
        )

    await coordinator.async_request_refresh()