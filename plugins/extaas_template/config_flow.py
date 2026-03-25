from homeassistant import config_entries
from .const import DOMAIN

class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_zeroconf(self, discovery_info):
        host = discovery_info.host
        port = discovery_info.port
        name = discovery_info.name

        unique_id = f"{host}:{port}"

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {
            "name": name
        }

        self._data = {
            "name": name,
            "host": host,
            "port": port
        }

        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=self._data["name"],
                data=self._data
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self._data["name"],
                "host": self._data["host"]
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