# update.py
import logging
import os
from homeassistant.helpers.entity import Entity
from .coordinator import ExtaasCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_update_data(coordinator: ExtaasCoordinator):
    if not coordinator:
        raise ValueError("Coordinator is required for update")
    _LOGGER.debug("Updating data via ExtaasCoordinator")
    return await coordinator._async_update_data()


# -------------------------
# Update-check entity
# -------------------------
class XEntitiesUpdateEntity(Entity):
    """Entity, mis näitab plugin update olemasolu."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._state = None
        self._name = "X Entities Update"
        self._unique_id = f"x_entities_update_{entry.entry_id}"

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        return self._state

    async def async_update(self):
        try:
            plugin_dir = "/homeassistant/custom_components/x_entities"
            update_file = os.path.join(plugin_dir, ".update_available")
            self._state = os.path.exists(update_file)
        except Exception as e:
            _LOGGER.error("X Entities update entity failed: %s", e)
            self._state = None