from homeassistant.helpers import device_registry as dr, entity_registry as er
from ..const import DOMAIN

async def create_device_with_entities(hass, entry, host, port, hostname, service_name, dynamic_items):
    """Loob parent device, child device ja heartbeat + dünaamilised entity-d."""
    registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    # Parent
    parent = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, host)},
        name=hostname,
        manufacturer="Extaas",
        model="Host"
    )

    # Child
    child = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{host}:{port}")},
        name=service_name,
        manufacturer="Extaas",
        model="Service",
        via_device=(DOMAIN, host)
    )

    # Heartbeat sensor
    heartbeat_id = f"{host}:{port}:heartbeat"
    entity_registry.async_get_or_create(
        "sensor",
        DOMAIN,
        heartbeat_id,
        device_id=child.id
    )

    # Dünaamilised entity-d
    for item in dynamic_items:
        unique_id = f"{host}:{port}:{item['name']}"
        entity_registry.async_get_or_create(
            item["type"],
            DOMAIN,
            unique_id,
            device_id=child.id
        )

    return parent, child


async def create_dynamic_entities(hass, entry, host, port, child, node_data):
    """Loob dünaamilised entity-d JSON-listist."""
    entity_registry = er.async_get(hass)

    for item in node_data:
        unique_id = f"{host}:{port}:{item['name']}"
        entity_registry.async_get_or_create(
            item.get("type", "sensor"),
            DOMAIN,
            unique_id,
            device_id=child.id
        )


async def update_parent_child_devices(hass, entry, host: str, port: int, hostname: str, service_name: str):
    """Värskendab parent ja child device'id registry-s."""
    registry = dr.async_get(hass)

    parent = registry.async_get_device(identifiers={(entry.domain, host)})
    if parent:
        registry.async_update_device(parent.id, name=hostname)

    child = registry.async_get_device(identifiers={(entry.domain, f"{host}:{port}")})
    if child:
        registry.async_update_device(child.id, name=service_name)