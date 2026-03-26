from homeassistant import config_entries
import voluptuous as vol

class ExtaasOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("name", default=self.entry.data["name"]): str,
                vol.Required("host", default=self.entry.data["host"]): str,
                vol.Required("port", default=self.entry.data["port"]): int
            })
        )