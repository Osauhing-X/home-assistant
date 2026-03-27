import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Heartbeat poller for Node"""

    def __init__(self, hass, entry_id, host, port):
        self.hass = hass
        self.entry_id = entry_id
        self.host = host
        self.port = port
        super().__init__(
            hass,
            _LOGGER,
            name=f"{entry_id}:{port}",
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        url = f"http://{self.host}:{self.port}/heartbeat"
        try:
            async with async_timeout.timeout(5):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            raise UpdateFailed(f"Bad status {resp.status}")
                        data = await resp.json()
                        return data
        except Exception as e:
            _LOGGER.warning("Heartbeat fetch failed: %s", e)
            return {"ok": False}