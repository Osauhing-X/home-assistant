import logging
from datetime import timedelta
import async_timeout
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, HEARTBEAT_PATH

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Poll heartbeat from Node."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        cfg = entry.options or entry.data
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{cfg.get('name')}",
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        cfg = self.entry.options or self.entry.data
        url = f"http://{cfg['host']}:{cfg.get('port',3000)}{HEARTBEAT_PATH}"
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
            return {"ok": False, "status": "offline"}