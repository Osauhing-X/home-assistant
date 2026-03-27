import asyncio
import logging
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from .const import SIGNAL_NEW_DATA

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Koordineerib entry -> service device -> entity hierarhiat.
    Hallatakse heartbeat, dünaamilisi sensorid ja switchid, ning switchi update queue'd."""

    def __init__(self, hass: HomeAssistant, entry):
        """Init coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data.get("hostname", "Extaas Coordinator"),
            update_interval=None,  # Manuaalne refresh, mitte perioodiline
        )

        self.hass = hass
        self.entry = entry
        self.host = entry.data["host"]
        self.port = entry.data["port"]
        self.hostname = entry.data.get("hostname", self.host)
        self.node_name = entry.data.get("service_name", f"Service {self.port}")

        # Queue switch/update käskude jaoks
        self.todo_list = asyncio.Queue()

        # Dünaamilised entity-d tulevad API-st
        self.dynamic_entities = entry.data.get("dynamic_entities", [])

        # Heartbeat state
        self.heartbeat_state = None

        # Käivitame taustaloop
        self.hass.loop.create_task(self._process_todo_loop())

    async def _async_update_data(self):
        """DataUpdateCoordinator kohustuslik meetod."""
        try:
            await self.async_refresh_heartbeat()

            # Koosta dünaamiliste sensorite väärtused
            dynamic_data = {e["name"]: e.get("value", False) for e in self.dynamic_entities}

            return {
                "heartbeat": self.heartbeat_state,
                "dynamic_entities": dynamic_data,
            }
        except Exception as err:
            raise UpdateFailed(f"Failed to update Extaas data: {err}") from err

    # -------------------
    # Heartbeat
    # -------------------
    async def async_refresh_heartbeat(self):
        """Kontrollib heartbeat-i Node seadmelt."""
        url = f"http://{self.host}:{self.port}/heartbeat"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    text = await resp.text()
                    self.heartbeat_state = resp.status == 200 and text.strip() == "OK"
        except Exception as e:
            _LOGGER.warning("Heartbeat check failed: %s", e)
            self.heartbeat_state = False

    # -------------------
    # Switch/update queue
    # -------------------
    def add_to_todo(self, item: dict):
        """Lisa switchi/sensor update queue-sse."""
        self.todo_list.put_nowait(item)

    async def _process_todo_loop(self):
        """Taustal töötav loop switch/update queue jaoks."""
        while True:
            item = await self.todo_list.get()
            try:
                await self._send_update(item)
            except Exception as e:
                _LOGGER.error("Error sending update %s: %s", item, e)
            finally:
                self.todo_list.task_done()

    async def _send_update(self, item: dict):
        """Saadab switchi/sensor update Node API-le."""
        url = f"http://{item['host']}:{item['port']}/update"
        payload = {item["name"]: item["value"]}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    _LOGGER.warning("Update for %s failed: %s", item["name"], resp.status)

    # -------------------
    # Dünaamilised HA entity-d
    # -------------------
    def create_ha_entity(self, entity_data: dict, device_id: str):
        """Loo dünaamiline sensor või switch Entity HA-s."""
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
                """Switchi vajutus läheb läbi coordinatori queue."""
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