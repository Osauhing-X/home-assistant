from homeassistant.helpers.entity import SwitchEntity
from .helpers import build_entities
from .const import DOMAIN, SIGNAL_NEW_DATA
from homeassistant.helpers.dispatcher import async_dispatcher_connect

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities_data = [e for e in build_entities(entry, coordinator.node_full) if e["platform"]=="switch"]

    switches = [ExtaasDynamicSwitch(entry, coordinator, e) for e in entities_data]
    async_add_entities(switches)

class ExtaasDynamicSwitch(SwitchEntity):
    def __init__(self, entry, coordinator, entity_data):
        self._entry = entry
        self.coordinator = coordinator
        self._entity_data = entity_data
        self._attr_name = entity_data["name"]
        self._attr_unique_id = entity_data["unique_id"]
        self._device_info = entity_data["device_info"]
        self._is_on = entity_data.get("initial_value", False)

    @property
    def device_info(self):
        return self._device_info

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        await self.coordinator.add_todo(self._entity_data["key"], True)
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.add_todo(self._entity_data["key"], False)
        self._is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_NEW_DATA, self._update_state
            )
        )

    def _update_state(self, entry_id):
        if entry_id == self._entry.entry_id:
            key = self._entity_data["key"]
            self._is_on = self.coordinator.node_data.get(key, False)
            self.async_write_ha_state()