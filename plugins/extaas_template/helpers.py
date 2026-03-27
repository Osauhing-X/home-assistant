from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription

PLATFORM_MAP = {
    "sensor": SensorEntityDescription,
    "switch": SwitchEntityDescription,
}

def build_device_hierarchy(entry, node_full):
    host = entry.data["host"]
    port = entry.data["port"]

    hostname = entry.data.get("hostname") or host
    service_name = entry.data.get("name")  # Discord / Website

    # 🔥 GROUP (host level)
    parent_device_info = {
        "identifiers": {(entry.domain, host)},
        "name": hostname,
        "manufacturer": "Extaas",
        "model": "Host",
    }

    # 🔥 CHILD DEVICE (service / port level)
    child_device_info = {
        "identifiers": {(entry.domain, f"{host}:{port}")},
        "name": service_name,
        "manufacturer": "Extaas",
        "model": "Service",
        "via_device": (entry.domain, host),
    }

    entities = []

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

    return parent_device_info, child_device_info, entities