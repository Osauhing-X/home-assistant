from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Manuaalne lisamine."""
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

    async def async_step_discovery(self, user_input=None):
        """Auto-discovery samm."""
        store = self.hass.data.get(DOMAIN, {})
        discovered_nodes = store.get("discovered", {})

        if not discovered_nodes:
            return self.async_abort(reason="no_discovered")

        # Kui kasutaja valib node
        if user_input:
            node_id = user_input["node"]
            node_data = discovered_nodes[node_id]
            return self.async_create_entry(
                title=node_data.get("name", node_id),
                data=node_data
            )

        # Kuva valikud UI-s
        nodes = {k: v.get("name", k) for k, v in discovered_nodes.items()}
        return self.async_show_form(
            step_id="discovery",
            data_schema=vol.Schema({
                vol.Required("node"): vol.In(nodes)
            })
        )

    @staticmethod
    def async_get_options_flow(entry):
        from .options_flow import OptionsFlow
        return OptionsFlow(entry)