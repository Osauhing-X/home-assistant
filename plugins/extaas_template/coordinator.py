import asyncio
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, SIGNAL_UPDATE

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Koordineerib entry -> device -> entity hierarhiat."""

    def __init__(self, hass: HomeAssistant, entry):
        name = entry.data.get("service_name", "Extaas Coordinator")
        super().__init__(hass, _LOGGER, name=name, update_interval=None)
        self.hass = hass
        self.entry = entry
        self.host = entry.data.get("host")
        self.port = entry.data.get("port")
        self.todo_list = asyncio.Queue()
        self.dynamic_entities = []
        self.heartbeat_state = None

        if self.host and self.port:
            self.hass.loop.create_task(self._process_todo_loop())

    async def _async_update_data(self):
        try:
            await self.async_refresh_heartbeat()
            dynamic_data = {e["name"]: e.get("value", False) for e in self.dynamic_entities}
            return {"heartbeat": self.heartbeat_state, "dynamic_entities": dynamic_data}
        except Exception as err:
            raise UpdateFailed(f"Failed to update Extaas data: {err}") from err

    async def async_refresh_heartbeat(self):
        prev = self.heartbeat_state
        self.heartbeat_state = False
        url = f"http://{self.host}:{self.port}/heartbeat"

        try:
            session = self.hass.data[DOMAIN]["runtime"]["session"]
            async with session.get(url, timeout=5) as resp:
                text = await resp.text()
                self.heartbeat_state = resp.status == 200 and text.strip() == "OK"
        except Exception:
            self.heartbeat_state = False

        if prev != self.heartbeat_state:
            _LOGGER.info("Node %s:%s is now %s", self.host, self.port,
                         "ONLINE" if self.heartbeat_state else "OFFLINE")

        async_dispatcher_send(self.hass, SIGNAL_UPDATE, self.entry.entry_id, {"heartbeat"})

    def add_to_todo(self, item: dict):
        self.todo_list.put_nowait(item)

    async def _process_todo_loop(self):
        while True:
            item = await self.todo_list.get()
            try:
                await self._send_update(item)
            except Exception as e:
                _LOGGER.error("Error sending update %s: %s", item, e)
            finally:
                self.todo_list.task_done()

    async def _send_update(self, item: dict):
        url = f"http://{item.get('host')}:{item.get('port')}/update"
        payload = {item["name"]: item["value"]}
        try:
            session = self.hass.data[DOMAIN]["runtime"]["session"]
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    _LOGGER.warning("Update failed for %s: %s", item["name"], resp.status)
        except Exception as e:
            _LOGGER.warning("Error sending update %s: %s", item["name"], e)