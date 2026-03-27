import asyncio
import aiohttp
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import SIGNAL_NEW_DATA

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Haldb heartbeat ja nodeData värskendust."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.host = entry.data.get("host")
        self.port = entry.data.get("port")
        self.node_name = entry.data.get("name") or self.host
        self.hostname = entry.data.get("hostname") or self.host

        self.node_data = {"heartbeat": False}
        self.node_full = {}
        self.todo_list = []

        super().__init__(
            hass,
            _LOGGER,
            name=f"{self.node_name}_coordinator",
            update_interval=timedelta(seconds=10)
        )

    async def _async_update_data(self):
        try:
            heartbeat = await self._get_heartbeat()
            self.node_data["heartbeat"] = heartbeat

            if "nodeData" not in self.node_full:
                self.node_full["nodeData"] = []

            async_dispatcher_send(self.hass, SIGNAL_NEW_DATA, self.entry.entry_id)
            return self.node_data

        except Exception as e:
            raise UpdateFailed(f"Heartbeat error for {self.node_name}: {e}")

    async def _get_heartbeat(self):
        url = f"http://{self.host}:{self.port}/heartbeat"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("heartbeat", True)
                    return True
            except Exception as e:
                _LOGGER.error("Heartbeat error for %s (%s:%s): %s", self.node_name, self.host, self.port, e)
                return False

    async def process_todo_list(self):
        while self.todo_list:
            task = self.todo_list.pop(0)
            key, value = next(iter(task.items()))
            url = f"http://{self.host}:{self.port}/update"
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(url, json={key: value}, timeout=5) as resp:
                        if resp.status == 200:
                            self.node_data[key] = value
                            _LOGGER.debug("Updated %s=%s on node %s", key, value, self.node_name)
                        else:
                            _LOGGER.error("Failed update %s=%s for %s: %s", key, value, self.node_name, resp.status)
                except Exception as e:
                    _LOGGER.error("Exception during update %s=%s for %s: %s", key, value, self.node_name, e)

    async def add_todo(self, key, value):
        self.todo_list.append({key: value})
        await self.process_todo_list()