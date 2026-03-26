from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Setup sensors."""

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # --- DEVICE GROUP (IP põhine) ---
    device_info = {
        "identifiers": {(entry.domain, coordinator.host)},
        "name": coordinator.node_name,
        "manufacturer": "Extaas",
        "model": "Node Device",
    }

    sensors = []

    # --- HEARTBEAT SENSOR ---
    sensors.append(
        ExtaasSensor(coordinator, device_info, "heartbeat")
    )

    async_add_entities(sensors)


class ExtaasSensor(CoordinatorEntity, SensorEntity):
    """Heartbeat sensor (ja tulevikus muud sensorid)."""

    def __init__(self, coordinator, device_info, sensor_name):
        super().__init__(coordinator)

        self._device_info = device_info
        self._name = sensor_name

        self._attr_unique_id = f"{coordinator.host}_{sensor_name}"
        self._attr_name = f"{coordinator.node_name} {sensor_name}"

    @property
    def native_value(self):
        """Väärtus tuleb coordinatorist."""
        if self._name == "heartbeat":
            return self.coordinator.data

        return None  # placeholder future jaoks

    @property
    def device_info(self):
        """Seob sensori device'iga."""
        return self._device_info

    @property
    def should_poll(self):
        return False