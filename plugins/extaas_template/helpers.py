from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription

PLATFORM_MAP = {
    "sensor": SensorEntityDescription,
    "switch": SwitchEntityDescription
}

def build_device_hierarchy(entry, node_full):
    """
    Tagastab child device info + entity list.
    Alati lisab heartbeat sensor.
    """
    host = entry.data["host"]
    port = entry.data["port"]
    service_name = entry.data.get("name")

    # Child device info (service/port)
    child_device_info = {
        "identifiers": {(entry.domain, f"{host}:{port}")},
        "name": service_name,
        "manufacturer": "Extaas",
        "model": "Service",
    }

    # Heartbeat sensor alati olemas
    entities = [{
        "platform": "sensor",
        "key": "heartbeat",
        "unique_id": f"{host}:{port}_heartbeat",
        "name": "Heartbeat",
        "device_info": child_device_info,
        "entity_description": SensorEntityDescription(
            key="heartbeat",
            name="Heartbeat",
            icon="mdi:heart-pulse",
        ),
    }]

    # Dünaamilised nodeData entity-d
    for key, cfg in node_full.items():
        entity_type = cfg.get("type", "sensor")
        icon = cfg.get("icon")
        description_cls = PLATFORM_MAP.get(entity_type, SensorEntityDescription)
        entities.append({
            "platform": entity_type,
            "key": key,
            "unique_id": f"{host}:{port}_{key}",
            "name": key.capitalize(),
            "device_info": child_device_info,
            "entity_description": description_cls(
                key=key,
                name=key.capitalize(),
                icon=icon,
            ),
        })

    return child_device_info, entities