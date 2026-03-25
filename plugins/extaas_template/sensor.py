from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    store = hass.data[DOMAIN]["store"]

    entities = []

    def update_entities(node):
        node_data = store.get_node(node)
        new_entities = []

        # node_data = { "Website": { heartbeat: {...}, port: {...}, ...}, "API": {...} }
        for service_name, service_obj in node_data.items():
            for key, value_obj in service_obj.items():
                entity_id = f"{node}_{service_name}_{key}"
                if entity_id not in data["entities"]:
                    ent = ServiceSensor(
                        coordinator, entry, node, service_name, key, value_obj
                    )
                    data["entities"][entity_id] = ent
                    new_entities.append(ent)

        if new_entities:
            async_add_entities(new_entities)

    hass.data[DOMAIN]["update_entities"] = update_entities
    update_entities(entry.data["name"])


class ServiceSensor(CoordinatorEntity, SensorEntity):
    """Üks teenus / seade grupi sees"""

    def __init__(self, coordinator, entry, node, service_name, key, value_obj):
        super().__init__(coordinator)
        self.node = node
        self.service_name = service_name
        self.key = key
        self.value_obj = value_obj if isinstance(value_obj, dict) else {"value": value_obj}

        self._attr_name = f"{service_name} {key}"
        self._attr_unique_id = f"{entry.entry_id}_{service_name}_{key}"

        # Device info - teenus on seade grupi sees
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{service_name}")},
            name=service_name,
            manufacturer="Extaas",
            model="Dynamic Service",
            via_device=(DOMAIN, entry.entry_id),
            configuration_url=f"http://{entry.data['host']}:{self.value_obj.get('value', 0)}"
        )

        # Icon fallbackiga
        self._icon = self.value_obj.get("icon") or "mdi:checkbox-blank-outline"

    @property
    def native_value(self):
        return self.value_obj.get("value")

    @property
    def icon(self):
        return self._icon