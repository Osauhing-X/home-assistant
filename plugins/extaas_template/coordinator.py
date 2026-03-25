import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .store import get_store

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.store = get_store(hass)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{entry.data['name']} Coordinator",
            update_interval=timedelta(seconds=10)
        )

    async def _async_update_data(self):
        # Heartbeat: True kui viimase nägemise timestamp < 15s
        heartbeat_last = self.store["last_seen"].get("heartbeat", 0)
        self.store["connected"]["heartbeat"] = (self.hass.loop.time() - heartbeat_last) < 15
        return {"ok": self.store["connected"].get("heartbeat", False)}