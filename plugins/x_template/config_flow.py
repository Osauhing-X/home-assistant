from homeassistant import config_entries

class ConfigFlow(config_entries.ConfigFlow, domain="x_template"):
    """GUI kaudu Node lisamise vorm"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "name": user_input["name"],
                    "host": user_input["host"],
                    "port": user_input.get("port", 3000)
                }
            )

        import voluptuous as vol
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("host"): str,
                vol.Optional("port", default=3000): int
            })
        )