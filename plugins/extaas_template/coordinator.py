from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Coordinator jälgib ainult heartbeat'i ühele IP:PORT seadmele."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.host = entry.data["host"]
        self.port = entry.data.get("port", 3000)
        self.node_name = entry.data["name"]
        self.heartbeat = False  # True kui status 200, False muidu

        super().__init__(
            hass,
            _LOGGER=_LOGGER,
            name=f"{self.node_name}_coordinator",
            update_interval=timedelta(seconds=5)
        )

    async def _async_update_data(self):
        """Kontrolli heartbeat."""
        url = f"http://{self.host}:{self.port}/heartbeat"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    self.heartbeat = resp.status == 200
            return self.heartbeat
        except Exception as err:
            self.heartbeat = False
            raise UpdateFailed(f"Heartbeat failed for {self.host}:{self.port} - {err}")