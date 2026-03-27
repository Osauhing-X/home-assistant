from homeassistant.helpers import entity_registry as er

async def async_cleanup_entities(hass, entry, valid_unique_ids):
    registry = er.async_get(hass)

    for entity in list(registry.entities.values()):
        if entity.config_entry_id != entry.entry_id:
            continue
        if entity.unique_id not in valid_unique_ids:
            registry.async_remove(entity.entity_id)