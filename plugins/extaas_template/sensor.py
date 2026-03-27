from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensorid (sh heartbeat ja dünaamilised sensorid)."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    child_device_id = hass.data[DOMAIN][entry.entry_id]["child_device_id"]

    entities = []

    # Dünaamilised sensorid
    for item in coordinator.dynamic_entities:
        if item.get("type") == "sensor":
            entities.append(coordinator.create_ha_entity(item, child_device_id))

    # Heartbeat sensor
    heartbeat_item = {
        "name": f"Heartbeat {coordinator.node_name}",
        "type": "sensor",
        "value": coordinator.heartbeat_state or False,
        "icon": "mdi:heart-pulse"
    }
    entities.append(coordinator.create_ha_entity(heartbeat_item, child_device_id))

    async_add_entities(entities, update_before_add=True)