import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, DEFAULT_PORT

class ExtaasOptionsFlowHandler(config_entries.OptionsFlow):
    """Manage options for Extaas integration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.data = dict(config_entry.data)

    async def async_step_init(self, user_input=None):
        if user_input:
            self.data.update(user_input)
            return self.async_create_entry(title="", data=self.data)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("name", default=self.data.get("name", "Unknown Device")): str,
                vol.Required("host", default=self.data.get("host", "0.0.0.0")): str,
                vol.Required("port", default=self.data.get("port", DEFAULT_PORT)): int
            })
        )