from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ExtaasOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        """Ära määra self.config_entry otse – ainult salvesta vajalikud andmed."""
        self._config_entry = config_entry  # PRIVATNE, mitte self.config_entry

    async def async_step_init(self, user_input=None):
        """Näita vormi options seadistamiseks."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("port", default=self._config_entry.options.get("port", 3000)): int,
                vol.Optional("name", default=self._config_entry.data.get("service_name", "Unknown")): str
            })
        )