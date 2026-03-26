import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class ExtaasOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow, mis võimaldab muuta Device Group nime ja IP-d."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        # Koopia olemasolevatest seadme andmetest
        self.data = dict(config_entry.data)

    async def async_step_init(self, user_input=None):
        """Esimene samm – vorm seadme redigeerimiseks"""
        if user_input is not None:
            # Salvestame uued väärtused entry.data-sse
            self.data["name"] = user_input["name"]
            self.data["host"] = user_input["host"]
            # Kutsume Home Assistant config_entry update
            return self.async_create_entry(title="", data=self.data)

        # Vorm koos praeguste väärtustega
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("name", default=self.data.get("name", "Unknown Device")): str,
                vol.Required("host", default=self.data.get("host", "0.0.0.0")): str,
                vol.Required("port", default=self.data.get("port", 3000)): int
            }),
        )