from homeassistant.helpers import device_registry as dr
from .entities import ExtaasDynamicEntity

class ExtaasDevicesManager:
    """Hallata entry -> device -> entity hierarhiat."""

    def __init__(self, hass, coordinator, entry_id):
        self.hass = hass
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.devices = {}  # device_id -> list of entity instances
        self.platforms = {}  # platform_name -> callback funktsioon

    def register_platform(self, platform_name, add_entities_callback):
        """Salvesta platvormi callback."""
        self.platforms[platform_name] = add_entities_callback

    def update_node_data(self, node_data):
        """Uuenda või loo seadmeid ja entity-d nodeData põhjal."""

        new_entities = []

        for d in node_data:
            device_id = f"{self.entry_id}_{self.coordinator.node_name}"
            if device_id not in self.devices:
                # Registreeri device HA-s
                dev_reg = dr.async_get(self.hass)
                dev_reg.async_get_or_create(
                    config_entry_id=self.entry_id,
                    identifiers={(self.entry_id, device_id)},
                    name=self.coordinator.node_name,
                    model="Extaas Node",
                    manufacturer="Extaas",
                )
                self.devices[device_id] = []

            # Kontrollime, kas entity juba olemas
            exists = any(e._attr_name == d["name"] for e in self.devices[device_id])
            if not exists:
                entity = ExtaasDynamicEntity(
                    self.coordinator,
                    self.entry_id,
                    self.coordinator.node_name,
                    d
                )
                self.devices[device_id].append(entity)
                new_entities.append(entity)

        # Lisa uued entity-d HA-sse läbi platvormi callback
        for entity in new_entities:
            platform = entity.entity_type  # "sensor" või "switch"
            if platform in self.platforms:
                self.hass.async_create_task(
                    self.platforms[platform]([entity])
                )