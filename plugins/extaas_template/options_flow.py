from homeassistant import config_entries
import voluptuous as vol

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_create_entry(title="", data=user_input)

        data = self.entry.options or self.entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("name", default=data.get("name")): str,
                vol.Required("host", default=data.get("host")): str,
                vol.Optional("port", default=data.get("port", 3000)): int
            })
        )