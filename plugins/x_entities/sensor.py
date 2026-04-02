# sensor.py
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .entities import ExtaasSensor
from .const import DOMAIN, SIGNAL_ENTITY, SIGNAL_UPDATE



class HeartbeatSensor(CoordinatorEntity, Entity):
    """Virtual Heartbeat sensor for each node entry"""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_heartbeat"
        self._attr_name = f"{entry.data.get('service_name', 'Node')} Heartbeat"
        self._attr_icon = "mdi:heart-pulse"
        self._attr_device_class = "connectivity"

        # Subscribe to dispatcher to update state
        self._unsub_dispatcher = async_dispatcher_connect(
            self.coordinator.hass,
            SIGNAL_UPDATE,
            self._async_handle_dispatch
        )

    @property
    def native_value(self):
        # Kui coordinator või heartbeat_state pole kätte saadav → False
        state = getattr(self.coordinator, "heartbeat_state", False)
        return bool(state)

    @property
    def available(self):
        return True

    async def _async_handle_dispatch(self, entry_id, updated_keys):
        if entry_id == self.entry.entry_id and "_heartbeat" in updated_keys:
            self.async_write_ha_state()
    
    async def async_will_remove_from_hass(self):
        if self._unsub_dispatcher:
            self._unsub_dispatcher()




async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]["entities"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # -------------------------
    # INITIAL LOAD
    # -------------------------
    entities = [
        HeartbeatSensor(coordinator, entry),

        ExtaasSensor(hass, entry, k)
        for k, v in data.items()
        if v.get("type") == "sensor"
    ]

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