async def async_setup_entry(hass, entry):
    store = hass.data[DOMAIN]

    # salvesta konfiguratsioon
    store["config"] = {
        "name": entry.data.get("name"),
        "host": entry.data.get("host"),
        "port": entry.data.get("port", 3000)
    }

    # Forward sensor platvorm
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True