from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta
from .store import get_store
from .const import DOMAIN

class ExtaasCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(
            hass,
            logger=hass.logger,
            name=f"{entry.entry_id} coordinator",
            update_interval=timedelta(seconds=5),
        )
        self.entry = entry

    async def _async_update_data(self):
        store = get_store(self.hass)
        node = self.entry.data["node"]
        return store["value"].get(node, {})