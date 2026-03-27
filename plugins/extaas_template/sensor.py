from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

from .const import DOMAIN, SIGNAL_UPDATE


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # 🔥 heartbeat alati olemas
    entities.append(HeartbeatSensor(coordinator, entry))

    # 🔥 dünaamilised sensorid
    for e in coordinator.entities:
        if e.get("type") != "switch":
            entities.append(DynamicSensor(coordinator, entry, e))

    async_add_entities(entities)

    # 🔥 heartbeat polling
    async def refresh(_):
        await coordinator.async_check_heartbeat()

    async_track_time_interval(hass, refresh, timedelta(seconds=10))


# --------------------------
# BASE
# --------------------------
class BaseEntity:
    def __init__(self, coordinator, entry, data=None):
        self.coordinator = coordinator
        self.entry = entry
        self.data = data or {}

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

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass,
            SIGNAL_UPDATE,
            self.async_write_ha_state
        )


# --------------------------
# HEARTBEAT
# --------------------------
class HeartbeatSensor(BaseEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)

        self._attr_name = f"{coordinator.name} Heartbeat"
        self._attr_unique_id = f"{entry.entry_id}_{coordinator.host}_{coordinator.port}_heartbeat"
        self._attr_icon = "mdi:heart-pulse"

    @property
    def native_value(self):
        return self.coordinator.heartbeat


# --------------------------
# DYNAMIC SENSOR
# --------------------------
class DynamicSensor(BaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, data):
        super().__init__(coordinator, entry, data)

        self._attr_name = data["name"]
        self._attr_unique_id = f"{entry.entry_id}_{coordinator.host}_{coordinator.port}_{data['name']}"
        self._attr_icon = data.get("icon")

    @property
    def native_value(self):
        for e in self.coordinator.entities:
            if e["name"] == self.data["name"]:
                return e.get("value")
        return None