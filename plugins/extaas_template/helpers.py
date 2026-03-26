from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription

def build_device_hierarchy(entry, node_data):
    """Loo Device Group -> Device -> Entities ühe funktsiooniga"""

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

    for node in node_data:
        key = node["name"]
        icon = node.get("icon")
        entity_type = node.get("type", "sensor")

        entity_info = {
            "unique_id": f"{entry.data['host']}:{entry.data['port']}_{key}",
            "name": f"{entry.data['name']} {key}",
            "device_info": child_device_info,
            "entity_description": None,
            "initial_value": node.get("value")
        }

        if entity_type == "sensor":
            entity_info["entity_description"] = SensorEntityDescription(
                key=key, name=key.capitalize(), icon=icon
            )
        elif entity_type == "switch":
            entity_info["entity_description"] = SwitchEntityDescription(
                key=key, name=key.capitalize(), icon=icon
            )

        entities.append(entity_info)

    return parent_device_info, child_device_info, entities