# sensor.py
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .entities import ExtaasSensor
from .const import DOMAIN, SIGNAL_ENTITY



class HeartbeatSensor(CoordinatorEntity, BinarySensorEntity):
    """Heartbeat sensor for each node entry"""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_heartbeat"
        self._attr_name = f"{entry.data.get('service_name', 'Node')} Heartbeat"
        self._attr_icon = "mdi:heart-pulse"
        self._attr_device_class = "connectivity"


    @property
    def is_on(self):
        # 👉 ALATI True/False (never unknown)
        return bool(getattr(self.coordinator, "heartbeat_state", False))
    
    @property
    def available(self):
        # 👉 alati olemas, isegi kui offline
        return True
    



async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]["entities"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # -------------------------
    # INITIAL LOAD
    # -------------------------
    entities = [ HeartbeatSensor(coordinator, entry) ] + [
        ExtaasSensor(hass, entry, k)
        for k, v in data.items()
        if v.get("type") == "sensor" ]

    async_add_entities(entities)

    # -------------------------
    # DYNAMIC ADD
    # -------------------------
    async def handle_new(eid, keys):
        if eid != entry.entry_id:
            return

        new = []
        current = hass.data[DOMAIN][entry.entry_id]["entities"]

        for k in keys:
            v = current.get(k)
            if not v or v.get("type") != "sensor":
                continue

            new.append(ExtaasSensor(hass, entry, k))

        if new:
            async_add_entities(new)

    async_dispatcher_connect(hass, SIGNAL_ENTITY, handle_new)