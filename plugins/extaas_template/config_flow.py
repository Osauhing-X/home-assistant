from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("host"): str,
                vol.Optional("port", default=3000): int
            })
        )

    @staticmethod
    def async_get_options_flow(entry):
        return OptionsFlow(entry)

class OptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Salvesta host/port muudatused
            data = dict(self.entry.data)
            data.update(user_input)
            self.entry.data = data
            return self.async_create_entry(title="", data=user_input)

        data = self.entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("host", default=data.get("host")): str,
                vol.Optional("port", default=data.get("port", 3000)): int
            })
        )