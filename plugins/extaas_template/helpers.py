from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription

def build_device_hierarchy(entry, node_full):
    """Tagastab device group (hostname) ja child device + entities list."""

    parent_device_info = {
        "identifiers": {(entry.domain, entry.data["host"])},
        "name": entry.data["host"],  # ⚡ Device Group = hostname/IP
        "manufacturer": "Extaas",
        "model": "Host",
    }

    entities = []

    node_data_list = node_full.get("nodeData", [])

    for node in node_data_list:
        key = node["name"]
        icon = node.get("icon")
        entity_type = node.get("type", "sensor")
        service_name = node.get("service_name") or key
        port = node.get("port", 3000)

        # Child device info
        child_device_info = {
            "identifiers": {(entry.domain, f"{entry.data['host']}:{port}")},
            "name": service_name,
            "manufacturer": "Extaas",
            "model": "Node Service",
            "via_device": (entry.domain, entry.data["host"]),
        }

        entity = {
            "unique_id": f"{entry.data['host']}:{port}_{key}",
            "name": f"{service_name} {key}",
            "key": key,
            "platform": entity_type,
            "device_info": child_device_info,
            "entity_description": None,
            "initial_value": node.get("value"),
        }

        if entity_type == "sensor":
            entity["entity_description"] = SensorEntityDescription(
                key=key,
                name=key.capitalize(),
                icon=icon
            )
        else:
            entity["entity_description"] = SwitchEntityDescription(
                key=key,
                name=key.capitalize(),
                icon=icon
            )

        entities.append(entity)

    return parent_device_info, entities