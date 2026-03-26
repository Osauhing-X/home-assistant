# plugins/extaas_template/coordinator.py
import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import HEARTBEAT_PATH, SCAN_INTERVAL

# Kindel, et logger on kehtiv
_LOGGER = logging.getLogger(__name__)
if _LOGGER is None:
    _LOGGER = logging.getLogger("extaas_template")

class ExtaasCoordinator(DataUpdateCoordinator):
    """Koordineerib heartbeat pollingut ja andmete uuendamist."""

    def __init__(self, hass, entry):
        self.host = entry.data["host"]
        self.port = entry.data["port"]

        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{entry.data.get('name', 'extaas_template')}_coordinator",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Heartbeat päring Node teenusele."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{self.host}:{self.port}{HEARTBEAT_PATH}", timeout=5) as resp:
                    return {"ok": resp.status == 200}
        except Exception as e:
            _LOGGER.debug("Heartbeat failed for %s:%s - %s", self.host, self.port, e)
            return {"ok": False}