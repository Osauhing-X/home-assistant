import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import HEARTBEAT_PATH, SCAN_INTERVAL

class ExtaasCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.host = entry.data["host"]
        self.port = entry.data["port"]

        super().__init__(
            hass,
            logger=hass.logger,
            name="extaas_template",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{self.host}:{self.port}{HEARTBEAT_PATH}",
                    timeout=5
                ) as resp:
                    return {"ok": resp.status == 200}
        except:
            return {"ok": False}