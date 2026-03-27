import asyncio
import logging
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Koordineerib seadme teenuseid, heartbeat ja dünaamilised entity-d."""

    def __init__(self, hass: HomeAssistant, entry):
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data.get("name", "Extaas Coordinator"),
            update_interval=None,  # Manuaalne refresh
        )

        self.hass = hass
        self.entry = entry
        self.host = entry.data["host"]
        self.port = entry.data["port"]
        self.node_name = entry.data.get("name", f"Service {self.port}")
        self.hostname = entry.data.get("hostname", self.host)

        # Queue switch/update päringute jaoks
        self.todo_list = asyncio.Queue()
        # Dünaamilised entity-d (sensorid/switchid)
        self.dynamic_entities = entry.data.get("dynamic_entities", [])
        # Heartbeat state
        self.heartbeat_state = None

        # Käivitame todo loopi taustal
        self.hass.loop.create_task(self._process_todo_loop())

    # -----------------------
    # Switch / Update Queue
    # -----------------------
    def add_to_todo(self, item: dict):
        """Lisa todo_listi (switch muudatused)."""
        self.todo_list.put_nowait(item)

    async def _process_todo_loop(self):
        """Töötlus tsükkel, mis teostab switch/update päringud järjest."""
        while True:
            todo_item = await self.todo_list.get()
            try:
                await self._send_update(todo_item)
            except Exception as e:
                _LOGGER.error("Viga todo_item '%s' saatmisel: %s", todo_item, e)
            finally:
                self.todo_list.task_done()

    async def _send_update(self, item: dict):
        """Teostab HTTP update request seadmele (switch/update)."""
        url = f"http://{item['host']}:{item['port']}/update"
        payload = {item["name"]: item["value"]}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    _LOGGER.warning(
                        "Update for %s failed: %s", item["name"], resp.status
                    )

    # -----------------------
    # Heartbeat
    # -----------------------
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

    # -----------------------
    # Dünaamilised entity-d
    # -----------------------
    def create_ha_entity(self, entity_data: dict, device_id: str):
        """Loob Home Assistant entity objekti (switch või sensor)."""

        coordinator = self  # et inner class pääseks coordinatorile ligi

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
                """Saada switchi väärtus coordinatorile ja uuenda HA state."""
                self_inner._attr_state = value
                item = {
                    "host": coordinator.host,
                    "port": coordinator.port,
                    "name": self_inner._entry_item["name"],
                    "value": value,
                }
                self_inner._coordinator.add_to_todo(item)
                self_inner.async_write_ha_state()

        return ExtaasDynamicEntity()

    # -----------------------
    # Required by DataUpdateCoordinator
    # -----------------------
    async def _async_update_data(self):
        """
        Kohustuslik meetod DataUpdateCoordinator jaoks.
        Siin tehakse heartbeat ja sensorite refresh.
        Tagastab dict, mis salvestatakse self.data alla.
        """
        await self.async_refresh_heartbeat()

        # Kogu dünaamiliste sensorite väärtused
        dynamic_data = {}
        for entity in self.dynamic_entities:
            dynamic_data[entity["name"]] = entity.get("value", False)

        return {
            "heartbeat": self.heartbeat_state,
            "dynamic_entities": dynamic_data,
        }

    # -----------------------
    # Full refresh kutsumine
    # -----------------------
    async def async_request_refresh(self):
        """Värskendab kõik dünaamilised entity-d ja heartbeat sensorid."""
        await self._async_update_data()
        self._async_update_listeners()