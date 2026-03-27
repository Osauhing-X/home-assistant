from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    child_device_id = hass.data[DOMAIN][entry.entry_id]["child_device_id"]

    entities = [
        coordinator.create_ha_entity(item, child_device_id)
        for item in coordinator.dynamic_entities
        if item["type"] == "switch"
    ]

    async_add_entities(entities)