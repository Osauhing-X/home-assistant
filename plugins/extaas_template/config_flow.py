from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN


class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Extaas."""
    VERSION = 1

    # =========================
    # MANUAL SETUP
    # =========================
    async def async_step_user(self, user_input=None):
        if user_input:
            host = user_input["host"]
            port = user_input["port"]

            # duplicate check (IP + PORT)
            for entry in self._async_current_entries():
                if entry.data.get("host") == host and entry.data.get("port") == port:
                    return self.async_abort(reason="already_configured")

            unique_id = f"{host}:{port}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input["service_name"],
                data={
                    "service_name": user_input["service_name"],
                    "host": host,
                    "port": port,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("service_name"): str,
                vol.Required("host"): str,
                vol.Required("port", default=3000): int,
            }),
        )

    # =========================
    # ZEROCONF AUTO DISCOVERY
    # =========================
    async def async_step_zeroconf(self, discovery_info):
        props_raw = discovery_info.properties or {}

        # decode bytes → str
        props = {
            (k.decode() if isinstance(k, bytes) else k):
            (v.decode() if isinstance(v, bytes) else v)
            for k, v in props_raw.items()
        }

        service_name = (props.get("service_name") or discovery_info.name).split("._")[0]
        host = props.get("host") or discovery_info.host
        port = discovery_info.port

        # duplicate check
        for entry in self._async_current_entries():
            if entry.data.get("host") == host and entry.data.get("port") == port:
                return self.async_abort(reason="already_configured")

        # unique id
        unique_id = f"{host}:{port}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        # 🔥 AUTO CREATE (NO CONFIRM)
        return self.async_create_entry(
            title=service_name,
            data={
                "service_name": service_name,
                "host": host,
                "port": port,
            },
        )

    # =========================
    # OPTIONS FLOW LINK
    # =========================
    @staticmethod
    def async_get_options_flow(config_entry):
        return ExtaasOptionsFlowHandler(config_entry)


# =========================
# OPTIONS FLOW
# =========================
class ExtaasOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Extaas."""

    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self._entry.options or self._entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "service_name",
                    default=data.get("service_name", "Extaas Node")
                ): str,
                vol.Optional(
                    "host",
                    default=data.get("host")
                ): str,
                vol.Optional(
                    "port",
                    default=data.get("port", 3000)
                ): int,
            }),
        )