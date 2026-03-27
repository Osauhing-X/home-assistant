from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    child_device_id = hass.data[DOMAIN][entry.entry_id]["child_device_id"]

    entities = [
        coordinator._create_ha_entity(item, child_device_id)
        for item in coordinator.dynamic_entities
        if item["type"] == "sensor"
    ]

    # Heartbeat sensor
    entities.append(
        coordinator._create_ha_entity(
            {"name": f"Heartbeat {coordinator.node_name}", "type": "sensor", "icon": "mdi:heart-pulse"},
            child_device_id
        )
    )

    async_add_entities(entities)