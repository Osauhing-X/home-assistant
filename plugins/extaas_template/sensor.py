from homeassistant.components.sensor import SensorEntity

class ExtaasSensor(SensorEntity):
    """Dünaamiline sensor seadmele."""

    def __init__(self, coordinator, device_info, sensor_name, sensor_type):
        self.coordinator = coordinator
        self._device_info = device_info
        self._name = sensor_name
        self._type = sensor_type

        self._attr_unique_id = f"{coordinator.node_name}_{sensor_name}"
        self._attr_name = f"{coordinator.node_name} {sensor_name}"

    @property
    def native_value(self):
        if self._name == "heartbeat":
            return self.coordinator.heartbeat
        return self.coordinator.node_data.get(self._name)

    @property
    def device_info(self):
        """
        Device info määrab, millise "Device Group"/Device alla see sensor läheb
        - identifiers -> unikaalne identifikaator IP põhjal
        - name -> Device Group nimi (nt hostname)
        """
        return self._device_info

    async def async_update(self):
        await self.coordinator.async_request_refresh()