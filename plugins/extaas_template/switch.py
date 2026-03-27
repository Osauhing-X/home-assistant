from homeassistant.components.switch import SwitchEntity
from .entities import ExtaasDynamicEntity

class ExtaasSwitch(ExtaasDynamicEntity, SwitchEntity):
    """Dynamic switch entity."""

    @property
    def is_on(self):
        return self._attr_state