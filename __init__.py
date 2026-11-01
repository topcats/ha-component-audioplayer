from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_DEVICE_NAME,
    DEFAULT_NAME,
    DEFAULT_STATUS_INTERVAL_SECONDS,
    SUPPORTED_PLATFORMS,
)




async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the AudioPlayer integration from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the AudioPlayer integration."""
    return await hass.config_entries.async_unload_platforms(entry, SUPPORTED_PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
