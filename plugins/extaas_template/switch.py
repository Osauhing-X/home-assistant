from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Setup switches."""

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # --- DEVICE GROUP ---
    device_info = {
        "identifiers": {(entry.domain, coordinator.host)},
        "name": coordinator.node_name,
        "manufacturer": "Extaas",
        "model": "Node Device",
    }

    switches = []

    # ⚠️ hetkel demo switch (hiljem dünaamiline)
    switches.append(
        ExtaasSwitch(coordinator, device_info, "web")
    )

    async_add_entities(switches)


class ExtaasSwitch(CoordinatorEntity, ToggleEntity):
    """Switch entity, mis saadab Node'le update."""

    def __init__(self, coordinator, device_info, name):
        super().__init__(coordinator)

        self._device_info = device_info
        self._name = name
        self._state = False

        self._attr_unique_id = f"{coordinator.host}_{name}"
        self._attr_name = f"{coordinator.node_name} {name}"

    @property
    def is_on(self):
        return self._state

    @property
    def device_info(self):
        return self._device_info

    async def async_turn_on(self, **kwargs):
        await self._update_node(True)

    async def async_turn_off(self, **kwargs):
        await self._update_node(False)

    async def _update_node(self, value):
        """Saada update Node.js serverile."""
        url = f"http://{self.coordinator.host}:{self.coordinator.port}/update"

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={self._name: value}, timeout=5)

            self._state = value
            self.async_write_ha_state()

        except Exception as err:
            _LOGGER.error(f"Switch update failed: {err}")

    @property
    def should_poll(self):
        return False