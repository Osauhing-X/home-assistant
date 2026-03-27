import logging
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo

_LOGGER = logging.getLogger(__name__)

class ExtaasDevicesManager:
    """Haldab HA entitysid coordinatori kaudu."""

    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.entities = []

    async def async_add_entities(self, async_add_entities_callback, device_name="NodeDevice", entity_type=None):
        """Lisa Heartbeat + dünaamilised entityd seotud seadme alla."""

        # --- Heartbeat sensor (ainult sensor platvormil) ---
        if entity_type == "sensor":
            heartbeat = HeartbeatSensor(self.coordinator, device_name)
            async_add_entities_callback([heartbeat])
            self.entities.append(heartbeat)

        # --- Dünaamilised entityd ---
        dynamic_entities = []
        for e in self.coordinator.dynamic_entities:
            if e.get("type") == "switch" and (entity_type is None or entity_type=="switch"):
                dynamic_entities.append(DynamicSwitch(self.coordinator, device_name, e["name"]))
            elif e.get("type") != "switch" and (entity_type is None or entity_type=="sensor"):
                dynamic_entities.append(DynamicSensor(self.coordinator, device_name, e["name"]))

        if dynamic_entities:
            async_add_entities_callback(dynamic_entities)
            self.entities.extend(dynamic_entities)


# --------------------------
# Heartbeat sensor
# --------------------------
class HeartbeatSensor(SensorEntity):
    def __init__(self, coordinator, device_name):
        self.coordinator = coordinator
        self._name = f"{coordinator.node_name} Heartbeat"
        self._unique_id = f"{coordinator.entry.entry_id}:{device_name}:heartbeat"

        self._device_info = DeviceInfo(
            identifiers={(coordinator.entry.entry_id, device_name)},
            name=device_name,
            manufacturer="Extaas",
            model="Node Device",
        )
        self._icon = "mdi:heart-pulse"

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        return self._device_info

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return getattr(self.coordinator, "heartbeat_state", "unknown")

    async def async_update(self):
        if hasattr(self.coordinator, "async_refresh_heartbeat"):
            await self.coordinator.async_refresh_heartbeat()


# --------------------------
# Dünaamiline switch
# --------------------------
class DynamicSwitch(SwitchEntity):
    def __init__(self, coordinator, device_name, name):
        self.coordinator = coordinator
        self.device_name = device_name
        self._name = name
        self._is_on = False

        self._device_info = DeviceInfo(
            identifiers={(coordinator.entry.entry_id, device_name)},
            name=device_name,
            manufacturer="Extaas",
            model="Node Device",
        )

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"{self.coordinator.entry.entry_id}:{self.device_name}:{self._name}"

    @property
    def device_info(self):
        return self._device_info

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        self.async_write_ha_state()
        self.coordinator.add_to_todo({"name": self._name, "value": True})

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self.async_write_ha_state()
        self.coordinator.add_to_todo({"name": self._name, "value": False})


# --------------------------
# Dünaamiline sensor
# --------------------------
class DynamicSensor(SensorEntity):
    def __init__(self, coordinator, device_name, name):
        self.coordinator = coordinator
        self.device_name = device_name
        self._name = name

        self._device_info = DeviceInfo(
            identifiers={(coordinator.entry.entry_id, device_name)},
            name=device_name,
            manufacturer="Extaas",
            model="Node Device",
        )

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"{self.coordinator.entry.entry_id}:{self.device_name}:{self._name}"

    @property
    def device_info(self):
        return self._device_info

    @property
    def state(self):
        for e in self.coordinator.dynamic_entities:
            if e["name"] == self._name:
                return e.get("value", None)
        return None

    async def async_update(self):
        if hasattr(self.coordinator, "_async_update_data"):
            await self.coordinator._async_update_data()