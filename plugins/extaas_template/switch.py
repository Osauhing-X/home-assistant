from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, SIGNAL_UPDATE


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for e in coordinator.entities:
        if e.get("type") == "switch":
            entities.append(DynamicSwitch(coordinator, entry, e))

    async_add_entities(entities)


class DynamicSwitch(SwitchEntity):
    def __init__(self, coordinator, entry, data):
        self.coordinator = coordinator
        self.entry = entry
        self.data = data

        self._attr_name = data["name"]
        self._attr_unique_id = f"{entry.entry_id}_{coordinator.host}_{coordinator.port}_{data['name']}"
        self._attr_icon = data.get("icon")

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={
                (DOMAIN, f"{self.coordinator.host}:{self.coordinator.port}")
            },
            name=self.coordinator.name,
            manufacturer="Extaas",
            model="Node Service",
            via_device=(DOMAIN, self.entry.entry_id),
        )

    @property
    def is_on(self):
        for e in self.coordinator.entities:
            if e["name"] == self.data["name"]:
                return e.get("value", False)
        return False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_send_update(self.data["name"], True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_send_update(self.data["name"], False)

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass,
            SIGNAL_UPDATE,
            self.async_write_ha_state
        )