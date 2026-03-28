import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

class ExtaasCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry_id, host, port):
        self.host = host
        self.port = port

        super().__init__(
            hass,
            None,
            name=f"{host}:{port}",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"http://{self.host}:{self.port}/heartbeat") as r:
                    return r.status == 200
        except:
            return False