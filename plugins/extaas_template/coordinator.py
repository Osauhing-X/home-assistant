import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN
from .store import get_store

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=5),
        )
        self.data = get_store(hass)

    async def _async_update_data(self):
        for node in self.data["connected"]:
            last_seen = self.data["last_seen"].get(node)
            if last_seen is None:
                self.data["connected"][node] = False
        return self.data