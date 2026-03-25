from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN
from .store import get_store

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        store = get_store(self.hass)
        discovered_nodes = store.get("discovered", {})

        if user_input:
            node = user_input["node"]
            return self.async_create_entry(
                title=discovered_nodes[node]["name"],
                data={"node": node}
            )

        if not discovered_nodes:
            # Kui pole veel discovery, näita tühja sõnumit
            return self.async_show_form(
                step_id="user",
                description_placeholders={"message": "No nodes discovered yet."},
                data_schema=vol.Schema({})
            )

        nodes_schema = vol.Schema({
            vol.Required(node, default=info["name"]): str
            for node, info in discovered_nodes.items()
        })

        return self.async_show_form(
            step_id="user",
            data_schema=nodes_schema
        )

    @staticmethod
    def async_get_options_flow(entry):
        return OptionsFlow(entry)


class OptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_create_entry(title="", data=user_input)

        # Võta praegused väärtused kas options või entry.data
        data = self.entry.options or self.entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("name", default=data.get("name")): str,
                vol.Required("host", default=data.get("host", "127.0.0.1")): str,
                vol.Optional("port", default=data.get("port", 3000)): int
            })
        )