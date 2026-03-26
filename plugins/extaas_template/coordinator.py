import logging
import aiohttp
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class ExtaasCoordinator(DataUpdateCoordinator):
    """Vastutab ainult heartbeat (ja hiljem ka node_data) eest."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self.host = entry.data["host"]
        self.port = entry.data["port"]
        self.node_name = entry.data["hostname"]

        self.node_data = {}

        # ⚠️ üks shared session (väga oluline)
        self.session = aiohttp.ClientSession()

        super().__init__(
            hass,
            _LOGGER,
            name=f"{self.node_name}_coordinator",
            update_interval=timedelta(seconds=10),  # stabiilne
        )

    async def _async_update_data(self):
        """Heartbeat check."""
        url = f"http://{self.host}:{self.port}/heartbeat"

        try:
            async with self.session.get(url, timeout=5) as resp:
                return resp.status == 200

        except Exception as err:
            _LOGGER.warning(
                f"Heartbeat error for {self.node_name} ({self.host}:{self.port}): {err}"
            )
            return False