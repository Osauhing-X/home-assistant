import asyncio
import logging
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Koordineerib seadme teenuseid ja sensorid."""

    def __init__(self, hass, entry):
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data.get("name", "Extaas Coordinator"),
            update_interval=None
        )
        self.hass = hass
        self.entry = entry
        self.host = entry.data["host"]
        self.port = entry.data["port"]
        self.node_name = entry.data.get("name", f"Service {self.port}")
        self.hostname = entry.data.get("hostname", self.host)

        self.todo_list = asyncio.Queue()
        self.dynamic_entities = entry.data.get("dynamic_entities", [])
        self.heartbeat_state = None

        # Käivitame todo loopi taustal
        self.hass.loop.create_task(self._process_todo_loop())

    def add_to_todo(self, item: dict):
        """Lisa todo_listi (switch muudatused)."""
        self.todo_list.put_nowait(item)

    async def _process_todo_loop(self):
        """Töötlus tsükkel, mis teostab switch update päringud järjest."""
        while True:
            todo_item = await self.todo_list.get()
            try:
                await self._send_update(todo_item)
            except Exception as e:
                _LOGGER.error("Viga todo_item '%s' saatmisel: %s", todo_item, e)
            finally:
                self.todo_list.task_done()

    async def _send_update(self, item: dict):
        """Teostab HTTP update request seadmele (switch /update)."""
        url = f"http://{item['host']}:{item['port']}/update"
        payload = {item["name"]: item["value"]}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    _LOGGER.warning(
                        "Update for %s failed: %s", item["name"], resp.status
                    )

    async def async_refresh_heartbeat(self):
        """Kontrollib /heartbeat endpointi ja uuendab heartbeat sensor."""
        url = f"http://{self.host}:{self.port}/heartbeat"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    text = await resp.text()
                    self.heartbeat_state = resp.status == 200 and text.strip() == "OK"
        except Exception as e:
            _LOGGER.warning("Heartbeat check failed: %s", e)
            self.heartbeat_state = False

    async def async_request_refresh(self):
        """Värskendab kõik dünaamilised entity-d."""
        await self.async_refresh_heartbeat()
        # Dünaamilised sensorid/switchid
        for entity in self.dynamic_entities:
            entity_type = entity.get("type")
            value = entity.get("value", False)
            # Heartbeat sensor ei muutu siin, see on eraldi handled
            # TODO: Värskenda HA state (kas kasutada async_write_ha_state())
        # Võid kutsuda DataUpdateCoordinator'i `_async_update_listeners`
        self._async_update_listeners()