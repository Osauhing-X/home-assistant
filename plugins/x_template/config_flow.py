from homeassistant import config_entries

class ConfigFlow(config_entries.ConfigFlow, domain="x_template"):
    async def async_step_user(self, user_input=None):
        return self.async_create_entry(title="X Template", data={})