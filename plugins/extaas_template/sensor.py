from homeassistant.components.sensor import SensorEntity
from .entities import ExtaasDynamicEntity

class ExtaasSensor(ExtaasDynamicEntity, SensorEntity):
    """Dynamic sensor entity."""
    
    @property
    def native_value(self):
        return self._attr_state