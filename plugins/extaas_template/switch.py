from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup switchid (dünaamilised switchid)."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    child_device_id = hass.data[DOMAIN][entry.entry_id]["child_device_id"]

    entities = []

    for item in coordinator.dynamic_entities:
        if item.get("type") == "switch":
            entities.append(coordinator.create_ha_entity(item, child_device_id))

    async_add_entities(entities)