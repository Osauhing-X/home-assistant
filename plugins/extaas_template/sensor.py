async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data["extaas_template"][entry.entry_id]["devices_manager"]
    await manager.async_add_entities(async_add_entities, "sensor")