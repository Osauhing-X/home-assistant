from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import ExtaasCoordinator
from .helper import get_device_info
from .store import get_store

class XSensor(CoordinatorEntity, SensorEntity):
    """Dünaamiline sensor Node poolt saadetud andmetega."""

    def __init__(self, hass, entry, node, key=None):
        self.hass = hass
        self.entry = entry
        self.node = node
        self.key = key
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        super().__init__(coordinator)

        self._attr_name = f"{node} {key or 'Heartbeat'}"
        self._attr_unique_id = f"x_{entry.entry_id}_{node}_{key or 'heartbeat'}"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        if self.key:
            return data.get(self.key)
        return data.get("ok", False)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {"node": self.node, **{k: v for k, v in data.items() if k != "ok"}}

    @property
    def device_info(self):
        cfg = self.entry.options or self.entry.data
        return get_device_info(self.node, cfg)