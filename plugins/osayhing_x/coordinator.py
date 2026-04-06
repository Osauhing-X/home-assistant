# coordinator.py
import asyncio
import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Koordineerib entry -> device -> entity hierarhiat."""

    def __init__(self, hass: HomeAssistant, entry):
        name = entry.data.get("service_name", "Extaas Coordinator") if entry.data else "Extaas Coordinator"
        super().__init__(hass, _LOGGER, name=name, update_interval=timedelta(seconds=30))

        self.hass = hass
        self.entry = entry
        self.host = entry.data.get("host") if entry.data else None
        self.port = entry.data.get("port") if entry.data else None

        self.todo_list = asyncio.Queue()
        self.heartbeat_state = False
        self.dynamic_entities = []  # {'name': 'Switch 1', 'type': 'switch', 'value': False}
        

        if self.host and self.port:
            self.hass.loop.create_task(self._process_todo_loop())
        else:
            _LOGGER.warning("Coordinator initialized without host/port")

    async def _async_update_data(self):
        try:
            await self.async_refresh_heartbeat()
            dynamic_data = {e["name"]: e.get("value", False) for e in self.dynamic_entities}
            return {"heartbeat": self.heartbeat_state, "dynamic_entities": dynamic_data}
        except Exception as err:
            raise UpdateFailed(f"Failed to update Extaas data: {err}") from err

    async def async_refresh_heartbeat(self):
        """Kontrollib node heartbeat'i ja logib ainult state muutused."""
        if not self.host or not self.port:
            self.heartbeat_state = False
            return

        prev = self.heartbeat_state
        url = f"http://{self.host}:{self.port}/heartbeat"

        try:
            session = self.hass.data[DOMAIN]["_runtime"]["session"]
            async with session.get(url, timeout=10) as resp:
                text = await resp.text()
                self.heartbeat_state = resp.status == 200 and text.strip() == "OK"
        except Exception:
            self.heartbeat_state = False
        
        if prev != self.heartbeat_state:
            state_str = "ONLINE" if self.heartbeat_state else "OFFLINE"
            _LOGGER.info("Node %s:%s is now %s", self.host, self.port, state_str)


    def add_to_todo(self, item: dict):
        """Lisa switchi/sensor update queue-sse Node serverisse."""
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
        if not item.get("host") or not item.get("port"):
            _LOGGER.warning("Skipping update for invalid host/port: %s", item)
            return

        url = f"http://{item['host']}:{item['port']}/update"
        payload = {item["name"]: item["value"]}

        try:
            session = self.hass.data[DOMAIN]["_runtime"]["session"]
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    _LOGGER.warning("Update for %s failed: %s", item["name"], resp.status)
        except Exception as e:
            _LOGGER.warning("Error sending update %s: %s", item["name"], e)