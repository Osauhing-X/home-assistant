from homeassistant.helpers.entity import Entity
from .const import DOMAIN

async def async_setup_entry(hass, entry, coordinator):
    data = await coordinator._async_update_data()
    entities = []

    # Üks node = device
    device_id = entry.entry_id

    # Parent device = node
    parent_device = {"identifiers": {(DOMAIN, device_id)}, "name": entry.data["node_name"]}

    # Service device
    service_device = {"identifiers": {(DOMAIN, f"{device_id}_service")}, "name": entry.data["service_name"], "via_device": (DOMAIN, device_id)}

    # Heartbeat sensor
    entities.append(NodeSensor("Heartbeat Sensorid", True, "mdi:server", "connectivity", service_device))

    # Dünaamilised sensorid
    for item in data:
        entities.append(NodeSensor(item["name"], item["value"], item.get("icon", "mdi:checkbox-blank-outline"), item.get("device_class"), service_device))

    for ent in entities:
        hass.async_create_task(ent.async_added_to_hass())

    return entities


class NodeSensor(Entity):
    def __init__(self, name, state, icon, device_class, device_info):
        self._attr_name = name
        self._state = state
        self._icon = icon
        self._device_class = device_class
        self._attr_device_info = device_info
        self._attr_unique_id = f"{device_info['identifiers']}_{name}"

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self._icon

    @property
    def device_class(self):
        return self._device_class