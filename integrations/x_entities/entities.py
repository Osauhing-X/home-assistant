# entities.py
import time

from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import callback

from .const import APPLICATION_UNAVAILABLE_AFTER, DOMAIN, SIGNAL_UPDATE


class BaseEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self, hass, entry, key):
        self.hass = hass
        self.entry = entry
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"

        device_name = self.data.get("device") or entry.data.get("service_name")
        device_id = self.data.get("device_id") or device_name.lower().replace(" ", "_")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name,
            "manufacturer": "Osaühing X",
            "model": self.data.get("model") or "Service Device" }
        if self.data.get("configuration_url"):
            self._attr_device_info["configuration_url"] = self.data["configuration_url"]
        if self.data.get("via_device"):
            self._attr_device_info["via_device"] = (DOMAIN, self.data["via_device"])

    @property
    def data(self):
        return self.hass.data[DOMAIN][self.entry.entry_id]["entities"].get(self.key, {})

    # -------------------------
    # UI PROPS
    # -------------------------
    @property
    def name(self):
        return self.data.get("name", self.key)

    @property
    def icon(self):
        return self.data.get("icon")

    # -------------------------
    # AVAILABILITY (future ready)
    # -------------------------
    @property
    def available(self):
        if self.data.get("source_id", "hub") == "hub":
            return True
        if self.data.get("is_heartbeat"):
            return True
        last_seen = self.data.get("last_seen")
        try:
            return bool(last_seen and time.time() - float(last_seen) <= APPLICATION_UNAVAILABLE_AFTER)
        except (TypeError, ValueError):
            return False

    # -------------------------
    # LIVE UPDATE
    # -------------------------
    async def async_added_to_hass(self):
        @callback
        def update(eid, changed):
            if eid == self.entry.entry_id and self.key in changed:
                if self.key not in self.hass.data[DOMAIN][self.entry.entry_id]["entities"]:
                    registry = er.async_get(self.hass)
                    registry_entry = registry.async_get(self.entity_id)
                    device_id = registry_entry.device_id if registry_entry else None
                    if registry_entry:
                        registry.async_remove(self.entity_id)
                    if device_id and not er.async_entries_for_device(registry, device_id):
                        dr.async_get(self.hass).async_remove_device(device_id)
                    return
                self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, update)
        )


# -------------------------
# SENSOR
# -------------------------
class ExtaasSensor(BaseEntity):
    @property
    def state(self):
        return self.data.get("value")
    
    # device_class & unit
    @property
    def native_value(self):
        return self.data.get("value")

    @property
    def device_class(self):
        return self.data.get("device_class")

    @property
    def native_unit_of_measurement(self):
        return self.data.get("unit")

    @property
    def state_class(self):
        return self.data.get("state_class")


class ExtaasBinarySensor(BaseEntity, BinarySensorEntity):
    @property
    def is_on(self):
        return bool(self.data.get("value"))

    @property
    def device_class(self):
        return self.data.get("device_class")


# -------------------------
# SWITCH
# -------------------------
class ExtaasSwitch(BaseEntity, SwitchEntity):
    @property
    def is_on(self):
        return self.data.get("value")

    async def async_turn_on(self, **kwargs):
        await self._send(True)

    async def async_turn_off(self, **kwargs):
        await self._send(False)

    async def _send(self, value):
        session = self.hass.data[DOMAIN]["_runtime"]["session"]
        url = f"http://{self.data.get('command_host', self.entry.data['host'])}:{self.data.get('command_port', self.entry.data['port'])}/update"
        command_key = self.data.get("command_key", self.key)

        # 👉 optimistic UI
        self.data["value"] = value
        self.async_write_ha_state()

        try:
            async with session.post(url, json={command_key: value}, timeout=10) as resp:
                if resp.status != 200:
                    raise HomeAssistantError(f"Device returned HTTP {resp.status}")
        except Exception as err:
            # 👉 revert kui failib
            self.data["value"] = not value
            self.async_write_ha_state()

            raise HomeAssistantError(f"Failed to send switch update: {err}") from err


# -------------------------
# BUTTON
# -------------------------
class ExtaasButton(BaseEntity, ButtonEntity):
    async def async_press(self):
        session = self.hass.data[DOMAIN]["_runtime"]["session"]
        url = f"http://{self.data.get('command_host', self.entry.data['host'])}:{self.data.get('command_port', self.entry.data['port'])}/update"
        command_key = self.data.get("command_key", self.key)

        try:
            async with session.post(url, json={command_key: True}, timeout=10) as resp:
                if resp.status != 200:
                    raise HomeAssistantError(f"Device returned HTTP {resp.status}")
        except Exception as err:
            raise HomeAssistantError(f"Failed to press button: {err}") from err
