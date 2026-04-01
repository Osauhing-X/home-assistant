import logging
from .coordinator import ExtaasCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_update_data(coordinator: ExtaasCoordinator):
    """
    Update X Entities data via ExtaasCoordinator.
    Kasutab olemasolevat coordinatorit, ei muuda midagi muud.
    """
    if not coordinator:
        raise ValueError("Coordinator is required for update")

    _LOGGER.debug("Updating data via ExtaasCoordinator")
    return await coordinator._async_update_data()