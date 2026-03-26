import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import HEARTBEAT_PATH, SCAN_INTERVAL

# Logger peab alati olema
_LOGGER = logging.getLogger(__name__)
if _LOGGER is None:
    _LOGGER = logging.getLogger("extaas_template")

class ExtaasCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.host = entry.data["host"]
        self.port = entry.data["port"]

        super().__init__(
            hass,
            logger=_LOGGER,  # kindlasti kehtiv Logger
            name=f"{entry.data.get('name', 'extaas_template')}_coordinator",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{self.host}:{self.port}{HEARTBEAT_PATH}", timeout=5) as resp:
                    return {"ok": resp.status == 200}
        except Exception as e:
            _LOGGER.debug("Heartbeat failed: %s", e)
            return {"ok": False}