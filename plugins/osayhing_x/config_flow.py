# config_flow.py
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ExtaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Extaas devices."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Init flow data."""
        self._data = {}

    # =========================
    # USER SETUP
    # =========================
    async def async_step_user(self, user_input=None):
        """Manual setup by user."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data.get("service_name", "Extaas Node"),
                data=self._data,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("service_name", default="Extaas Node"): str,
                vol.Required("host", default=""): str,
                vol.Required("port", default=80): int,
            }),
        )

    # =========================
    # ZEROCONF DISCOVERY (WITH CONFIRM)
    # =========================
    async def async_step_zeroconf(self, discovery_info):
        _LOGGER.debug("discovery info:", discovery_info)

        """Handle zeroconf discovery."""
        host = discovery_info.host
        port = discovery_info.port
        txt = discovery_info.properties or {}
        
        # decode bytes → str
        import json; props = {}
        # filter out key "data"
        data_key = next((k for k in txt if "data" in k), None)
        if data_key:
            try:  props = json.loads(txt[data_key])
            except Exception: _LOGGER.warning("Failed to parse zeroconf txt data: %s", txt["data"])
        else: props = {}

        hostname = props.get("hostname") or f"{host}:{port}"
        service_name = (props.get("service_name") or discovery_info.name).split("._")[0]
        

        _LOGGER.debug("Zeroconf discovered: %s:%s (%s)", host, port, service_name)

        # duplicate check (IP + PORT)
        for entry in self._async_current_entries():
            if entry.data.get("host") == host and entry.data.get("port") == port:
                return self.async_abort(reason="already_configured")

        # unique id
        unique_id = f"{host}:{port}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()  # avoids ghost flow / UnknownFlow

        # UI jaoks (pealkiri)
        self.context["title_placeholders"] = {
            "name": f"{service_name} ({hostname})".strip() or "Extaas Node"}

        # salvesta ajutiselt
        self._data = {
            "hostname": hostname,
            "service_name": service_name,
            "host": host,
            "port": port }

        return await self.async_step_confirm()

    # =========================
    # CONFIRM SCREEN
    # =========================
    async def async_step_confirm(self, user_input=None):
        """Confirm discovered device with user."""
        # defensiivne check
        if not hasattr(self, "_data") or not self._data:
            return self.async_abort(reason="missing_data")

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data.get("hostname", "Extaas Node"),
                data=self._data,
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self._data.get("hostname", "Extaas Node"),
                "host": self._data.get("host", "unknown"),
                "port": self._data.get("port", 80), },
            data_schema=vol.Schema({
                vol.Required( "hostname", default=self._data.get("hostname", "Extaas Node") ): str,
                vol.Required( "host", default=self._data.get("host", "unknown") ): str,
                vol.Required( "port", default=self._data.get("port", 80) ): int, }),
        )