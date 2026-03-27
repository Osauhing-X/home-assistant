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

            # ❗ duplicate check (IP + PORT)
            for entry in self._async_current_entries():
                if entry.data.get("host") == host and entry.data.get("port") == port:
                    return self.async_abort(reason="already_configured")

            unique_id = f"{host}:{port}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input["service_name"],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("hostname"): str,
                vol.Required("service_name"): str,
                vol.Required("host"): str,
                vol.Required("port", default=3000): int,
            }),
        )

    # =========================
    # ZEROCONF AUTO DISCOVERY
    # =========================
    async def async_step_zeroconf(self, discovery_info):
        # TXT OBJECT
        props_raw = discovery_info.properties or {}
        props = { # decode bytes → str
            (k.decode() if isinstance(k, bytes) else k):
            (v.decode() if isinstance(v, bytes) else v)
            for k, v in props_raw.items() }

        # VALUES
        hostname = props.get("node_name") or discovery_info.hostname
        service_name = (props.get("service_name") or discovery_info.name).split("._")[0]
        host = props.get("host") or discovery_info.host
        port = discovery_info.port

        """ IS UNIQUE ?? 2FA """
         # 1️⃣ IP:PORT ?
        for entry in self._async_current_entries():
            if entry.data.get("host") == host and entry.data.get("port") == port:
                return self.async_abort(reason="already_configured")

        # 2️⃣ NAME:PORT
        unique_id = f"{host}:{port}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        """ AUTO DISCOVERY """
        self.context["title_placeholders"] = {
            "name": service_name or "X Device",
            "host": host or "Extaas",
            "port": port }

        """ REGISTER DEVICE """
        self._data = {
            "hostname": hostname,
            "service_name": service_name,
            "host": host,
            "port": port, }

        return await self.async_step_confirm()

    # =========================
    # CONFIRM SCREEN
    # =========================
    async def async_step_confirm(self, user_input=None):
        if user_input:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data["service_name"],
                data=self._data,
            )

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({
                vol.Required("service_name", default=self._data["service_name"]): str,
                vol.Required("host", default=self._data["host"]): str,
                vol.Required("port", default=self._data["port"]): int,
            }),
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
                vol.Required("service_name", default=data.get("service_name")): str,
                vol.Required("host", default=data.get("host")): str,
                vol.Required("port", default=data.get("port", 3000)): int,
            }),
        )