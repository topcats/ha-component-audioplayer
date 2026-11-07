from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
import homeassistant.helpers.config_validation as cv

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from .const import (
    DOMAIN,
    SYSTEM_PROTOCOL,
    SYSTEM_PORT,
    SYSTEM_STATUS_PATH,
    DEFAULT_STATUS_INTERVAL_SECONDS,
    MANUAL_MODE_LABELS,
    CONF_STATUS_INTERVAL,
)

SCAN_INTERVAL = timedelta(seconds=DEFAULT_STATUS_INTERVAL_SECONDS)



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AudioPlayer sensor from a config entry."""
    config = {**entry.data, **entry.options}
    await _async_add_status_sensor(
        hass,
        config[CONF_HOST],
        timedelta(seconds=config[CONF_STATUS_INTERVAL]),
        async_add_entities,
    )


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up the AudioPlayer status sensor."""
    host = cv.string(config[CONF_HOST])
    scan_interval = cv.time_period(config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL))
    await _async_add_status_sensor(hass, host, scan_interval, async_add_entities)


async def _async_add_status_sensor(
    hass: HomeAssistant,
    host: str,
    scan_interval: timedelta,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the coordinator and status sensor."""
    session = async_get_clientsession(hass)
    status_url = f"{SYSTEM_PROTOCOL}://{host}:{SYSTEM_PORT}{SYSTEM_STATUS_PATH}"

    async def async_update_data() -> Any:
        try:
            async with session.get(status_url, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Unable to fetch AudioPlayer status: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        logger=logging.getLogger(__name__),
        name="AudioPlayer status",
        update_method=async_update_data,
        update_interval=scan_interval,
    )
    await coordinator.async_refresh()
    async_add_entities([AudioPlayerStatusSensor(coordinator, host)])


class AudioPlayerStatusSensor(SensorEntity):
    """Expose the AudioPlayer JSON status feed as a sensor."""

    _attr_has_entity_name = True
    _attr_name = "Status"

    def __init__(self, coordinator: DataUpdateCoordinator[Any], host: str) -> None:
        self.coordinator = coordinator
        device_id = host.strip().lower()
        self._attr_unique_id = f"{device_id}_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=host,
            manufacturer="TheOwls",
            model="RPI AudioPlayer",
        )

    @property
    def native_value(self) -> str | int | float:
        """Return a useful scalar from the status payload."""
        data = self.coordinator.data
        if isinstance(data, dict):
            for key in ("status", "state", "mode"):
                value = data.get(key)
                if isinstance(value, (str, int, float)):
                    if key == "mode" and type(value) is int:
                        return MANUAL_MODE_LABELS.get(value, value)
                    return value
        return "online"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the complete JSON payload as entity attributes."""
        data = self.coordinator.data
        return data if isinstance(data, dict) else {"data": data}

    @property
    def available(self) -> bool:
        """Report availability based on the latest successful poll."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """Subscribe to coordinator updates."""
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_update))

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()
