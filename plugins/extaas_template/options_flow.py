from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, DEFAULT_PORT

class ExtaasOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required("name", default=self.config_entry.data.get("name")): str,
            vol.Required("host", default=self.config_entry.data.get("host")): str,
            vol.Required("port", default=self.config_entry.data.get("port", DEFAULT_PORT)): int
        })
        return self.async_show_form(step_id="init", data_schema=schema)