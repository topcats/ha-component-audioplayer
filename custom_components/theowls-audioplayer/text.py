from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AudioPlayerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up staged manual URL and metadata inputs."""
    coordinator: AudioPlayerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ManualTextEntity(coordinator, entry, "url", "manual_url", 2048),
            ManualTextEntity(coordinator, entry, "title", "manual_title", 255),
            ManualTextEntity(coordinator, entry, "image", "manual_image", 2048),
        ]
    )


class ManualTextEntity(CoordinatorEntity[AudioPlayerCoordinator], TextEntity):
    """Stage a manual URL, title, or image for a later mode selection."""

    _attr_has_entity_name = True
    _attr_mode = TextMode.TEXT
    _attr_native_min = 0

    def __init__(
        self,
        coordinator: AudioPlayerCoordinator,
        entry: ConfigEntry,
        field: str,
        translation_key: str,
        max_length: int,
    ) -> None:
        super().__init__(coordinator)
        self._field = field
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{entry.entry_id}_{translation_key}"
        self._attr_native_max = max_length
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="TheOwls",
            model="AudioPlayer",
        )

    @property
    def native_value(self) -> str:
        """Return the staged value or the value saved by the player."""
        value = self.coordinator.manual_value(self._field)
        return value if isinstance(value, str) else ""

    async def async_set_value(self, value: str) -> None:
        """Stage a value without changing the currently playing source."""
        self.coordinator.async_stage_manual_value(self._field, value)
        self.async_write_ha_state()
