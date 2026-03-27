import asyncio
import aiohttp
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Koordineerib seadme teenuseid, heartbeat ja dünaamilised entity-d."""

    def __init__(self, hass: HomeAssistant, entry):
        super().__init__(hass, _LOGGER, name=entry.data.get("name", "Extaas Coordinator"), update_interval=None)
        self.hass = hass
        self.entry = entry
        self.host = entry.data["host"]
        self.port = entry.data["port"]
        self.node_name = entry.data.get("name", f"Service {self.port}")
        self.hostname = entry.data.get("hostname", self.host)
        self.dynamic_entities = entry.data.get("dynamic_entities", [])
        self.heartbeat_state = None
        self.todo_list = asyncio.Queue()
        self.hass.loop.create_task(self._process_todo_loop())

    def add_to_todo(self, item: dict):
        self.todo_list.put_nowait(item)

    async def _process_todo_loop(self):
        while True:
            todo_item = await self.todo_list.get()
            try:
                await self._send_update(todo_item)
            except Exception as e:
                _LOGGER.error("Todo item error: %s", e)
            finally:
                self.todo_list.task_done()

    async def _send_update(self, item: dict):
        url = f"http://{item['host']}:{item['port']}/update"
        payload = {item["name"]: item["value"]}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    _LOGGER.warning("Update failed: %s %s", item["name"], resp.status)

    async def async_refresh_heartbeat(self):
        url = f"http://{self.host}:{self.port}/heartbeat"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    text = await resp.text()
                    self.heartbeat_state = resp.status == 200 and text.strip() == "OK"
        except Exception as e:
            _LOGGER.warning("Heartbeat failed: %s", e)
            self.heartbeat_state = False

    def create_ha_entity(self, entity_data: dict, device_id: str):
        coordinator = self

        class ExtaasDynamicEntity(Entity):
            def __init__(self_inner):
                self_inner._attr_name = entity_data["name"]
                self_inner._attr_unique_id = f"{coordinator.host}:{coordinator.port}:{entity_data['name']}"
                self_inner._attr_device_id = device_id
                self_inner._attr_icon = entity_data.get("icon")
                self_inner._attr_state = entity_data.get("value", False)
                self_inner._coordinator = coordinator
                self_inner._entry_item = entity_data

            @property
            def is_on(self_inner):
                return self_inner._attr_state

            async def async_turn_on(self_inner, **kwargs):
                await self_inner._async_toggle(True)

            async def async_turn_off(self_inner, **kwargs):
                await self_inner._async_toggle(False)

            async def _async_toggle(self_inner, value: bool):
                self_inner._attr_state = value
                self_inner._coordinator.add_to_todo({
                    "host": coordinator.host,
                    "port": coordinator.port,
                    "name": self_inner._entry_item["name"],
                    "value": value
                })
                self_inner.async_write_ha_state()

        return ExtaasDynamicEntity()