from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription

PLATFORM_MAP = {
    "sensor": SensorEntityDescription,
    "switch": SwitchEntityDescription,
}

def build_device_hierarchy(entry, node_full):
    parent_device_info = {
        "identifiers": {(entry.domain, entry.data["host"])},
        "name": entry.data.get("hostname") or entry.data["host"],
        "manufacturer": "Extaas",
        "model": "Host",
    }

    child_device_info = {
        "identifiers": {(entry.domain, f"{entry.data['host']}:{entry.data['port']}")},
        "name": entry.data["name"],
        "manufacturer": "Extaas",
        "model": "Node Service",
        "via_device": (entry.domain, entry.data["host"]),
    }

    entities = []

    for key, cfg in node_full.items():
        entity_type = cfg.get("type", "sensor")
        icon = cfg.get("icon")

        description_cls = PLATFORM_MAP.get(entity_type, SensorEntityDescription)

        entities.append({
            "platform": entity_type,
            "key": key,
            "unique_id": f"{entry.data['host']}:{entry.data['port']}_{key}",
            "name": f"{entry.data['name']} {key}",
            "device_info": child_device_info,
            "entity_description": description_cls(
                key=key,
                name=key.capitalize(),
                icon=icon,
            ),
        })

    return parent_device_info, child_device_info, entities