from homeassistant.helpers import device_registry as dr, entity_registry as er
from .const import DOMAIN

async def create_node_devices(hass, entry, node_info):
    """Loo HA devices hierarhia ja entity-d."""
    registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    host = node_info["host"]
    hostname = node_info.get("hostname", host)
    port = node_info["port"]
    service_name = node_info.get("name", f"Service {port}")
    dynamic_entities = node_info.get("dynamic_entities", [])

    # Parent device (host)
    parent = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, host)},
        name=hostname,
        manufacturer="Extaas",
        model="Node"
    )

    # Child device (port/service)
    child = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{host}:{port}")},
        name=service_name,
        manufacturer="Extaas",
        model="Service",
        via_device=(DOMAIN, host)
    )

    # Heartbeat sensor
    entity_registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{host}:{port}:heartbeat",
        device_id=child.id,
        name="Heartbeat",
        icon="mdi:heart-pulse"
    )

    # Dünaamilised entity-d
    for item in dynamic_entities:
        entity_registry.async_get_or_create(
            item.get("type", "sensor"),
            DOMAIN,
            f"{host}:{port}:{item['name']}",
            device_id=child.id,
            name=item["name"],
            icon=item.get("icon")
        )

    return {"parent_device": parent, "child_device": child, "dynamic_entities": dynamic_entities}

async def update_node_devices(hass, entry, node_obj, new_info):
    """Värskendab device ja entity-d."""
    registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    child_id = node_obj["child_device"]

    # Update child device nimi
    registry.async_update_device(child_id, name=new_info.get("service_name"))

    # Dünaamilised entity-d
    for item in new_info.get("dynamic_entities", []):
        entity_registry.async_get_or_create(
            item.get("type", "sensor"),
            DOMAIN,
            f"{new_info['host']}:{new_info['port']}:{item['name']}",
            device_id=child_id,
            name=item["name"],
            icon=item.get("icon")
        )

    return new_info