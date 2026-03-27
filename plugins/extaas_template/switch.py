from homeassistant.helpers.entity import CoordinatorEntity, SwitchEntity
from .coordinator import ExtaasCoordinator
import logging

_LOGGER = logging.getLogger(__name__)

class ExtaasDynamicSwitch(CoordinatorEntity, SwitchEntity):
    """Dünaamiline switch, mis saadab muutuse coordinatorile todo_listi kaudu."""

    def __init__(self, coordinator: ExtaasCoordinator, host, port, item):
        super().__init__(coordinator)
        self.coordinator: ExtaasCoordinator = coordinator
        self.host = host
        self.port = port
        self.item = item

        self._attr_name = item["name"]
        self._attr_icon = item.get("icon")
        self._state = item.get("value", False)

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        self._state = True
        self.async_write_ha_state()
        await self._notify_coordinator(True)

    async def async_turn_off(self, **kwargs):
        self._state = False
        self.async_write_ha_state()
        await self._notify_coordinator(False)

    async def _notify_coordinator(self, value: bool):
        """
        Lisab switchi muudatuse coordinator.todo_list-i.
        Coordinator teeb ise järjekorras /update päringu seadmele.
        """
        todo_item = {
            "host": self.host,
            "port": self.port,
            "name": self.item["name"],
            "type": "switch",
            "value": value
        }

        # Lisame todo_listi
        self.coordinator.add_to_todo(todo_item)
        _LOGGER.debug(
            "Switch '%s' muudatus (%s) lisatud coordinator todo_listi",
            self.item["name"], value
        )