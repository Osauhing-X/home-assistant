from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription

def build_entities(entry, node_full):
    """
    Tagastab dünaamilised sensorid ja switchid iga child device (port) jaoks
    """
    entities = []

    for node in node_full.get("nodeData", []):
        port = node.get("port")
        service_name = node.get("service_name", f"Service {port}")
        for sensor in node.get("sensors", []):
            key = sensor["name"]
            entity_type = sensor.get("type", "sensor")
            icon = sensor.get("icon")

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
                "initial_value": sensor.get("value"),
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

    return entities