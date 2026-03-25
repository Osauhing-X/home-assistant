import logging
import asyncio
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .helper import update_last_seen, get_device_info
from .store import get_store

_LOGGER = logging.getLogger(__name__)

class ExtaasCoordinator(DataUpdateCoordinator):
    """Coordinatori klass Node heartbeat ja entity-de halduseks."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.node = entry.data["node"]
        self.store = get_store(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=f"Extaas {self.node}",
            update_interval=5.0,  # heartbeat kontrolli sagedus
        )

    async def _async_update_data(self):
        """Kontrolli heartbeat."""
        node_data = self.store.get("entities", {}).get(self.node, {})
        # Heartbeat False kui pole
        heartbeat = self.store["connected"].get(self.node, False)
        update_last_seen(self.hass, self.node)
        return {"ok": heartbeat, **node_data}