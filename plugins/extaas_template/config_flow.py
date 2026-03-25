from homeassistant import config_entries
from .const import DOMAIN

class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_zeroconf(self, discovery_info):
        return self.async_create_entry(
            title=discovery_info.name,
            data={
                "name": discovery_info.name,
                "host": discovery_info.host,
                "port": discovery_info.port
            }
        )

    async def async_step_user(self, user_input=None):
        import voluptuous as vol

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
                vol.Required("port"): int
            })
        )