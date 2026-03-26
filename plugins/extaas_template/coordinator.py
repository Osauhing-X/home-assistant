from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from datetime import timedelta
from .const import SCAN_INTERVAL

class ExtaasDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry):
        super().__init__(
            hass,
            _LOGGER := hass.logger,
            name=entry.title,
            update_interval=timedelta(seconds=SCAN_INTERVAL)
        )
        self.entry = entry
        self.node_data = []

    async def _async_update_data(self):
        # Siia tuleb reaalse API fetch logika
        # Näide sensoritest:
        return [
            {"name": "heartbeat", "value": True, "device_class": "connectivity"},
            {"name": "update_available", "value": False, "device_class": "update"}
        ]