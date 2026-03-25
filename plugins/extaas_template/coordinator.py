import logging
import async_timeout
import aiohttp
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class ExtaasCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,  # ✅ FIX
            name="extaas_template",
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        cfg = self.entry.options or self.entry.data
        url = f"http://{cfg['host']}:{cfg['port']}/health"

        try:
            async with async_timeout.timeout(5):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            raise UpdateFailed(f"Bad status: {resp.status}")

                        data = await resp.json()
                        return data

        except Exception as e:
            _LOGGER.error("Coordinator fetch failed: %s", e)
            raise UpdateFailed(str(e))