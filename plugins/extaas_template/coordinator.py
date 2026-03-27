import logging
import aiohttp
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import SIGNAL_UPDATE

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator:
    """Haldab state + suhtlust Node'iga."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self.host = entry.data["host"]
        self.port = entry.data["port"]
        self.name = entry.data.get("service_name", "Node")

        self.entities = []
        self.heartbeat = False

    # ------------------------
    # API → HA
    # ------------------------
    def update_from_api(self, data):
        self.entities = data.get("node_data", [])
        async_dispatcher_send(self.hass, SIGNAL_UPDATE, self.entry.entry_id)

    # ------------------------
    # HA → Node (heartbeat)
    # ------------------------
    async def async_check_heartbeat(self):
        url = f"http://{self.host}:{self.port}/heartbeat"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    data = await resp.json()
                    self.heartbeat = resp.status == 200 and data.get("ok", False)
        except Exception:
            self.heartbeat = False

        async_dispatcher_send(self.hass, SIGNAL_UPDATE, self.entry.entry_id)

    # ------------------------
    # HA → Node (switch)
    # ------------------------
    async def async_send_update(self, name, value):
        url = f"http://{self.host}:{self.port}/update"
        payload = {name: value}

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(url, json=payload, timeout=5)
        except Exception as e:
            _LOGGER.warning("Update failed: %s", e)