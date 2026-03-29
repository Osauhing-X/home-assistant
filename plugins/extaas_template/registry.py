from homeassistant.helpers import entity_registry as er
import logging

_LOGGER = logging.getLogger(__name__)

async def async_cleanup_entities(hass, entry, valid_unique_ids: set):
    """Eemalda kõik entry entityd, mis ei kuulu enam aktiivsete unikaalsete id-de hulka."""
    registry = er.async_get(hass)

    for entity in list(registry.entities.values()):
        if entity.config_entry_id != entry.entry_id:
            continue
        if entity.unique_id not in valid_unique_ids:
            _LOGGER.debug("Removing stale entity: %s", entity.entity_id)
            registry.async_remove(entity.entity_id)