from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN
from .options_flow import OptionsFlowHandler

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input
            )

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
        return OptionsFlowHandler(entry)