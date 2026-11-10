from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_LABELS
from .coordinator import AudioPlayerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up manual mode and source selectors."""
    coordinator: AudioPlayerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [ManualModeSelect(coordinator, entry), ManualSourceSelect(coordinator, entry)]
    )


class _AudioPlayerSelect(CoordinatorEntity[AudioPlayerCoordinator], SelectEntity):
    """Base entity for player selectors."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: AudioPlayerCoordinator, entry: ConfigEntry, key: str
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="TheOwls",
            model="AudioPlayer",
        )


class ManualModeSelect(_AudioPlayerSelect):
    """Select one of the player's documented manual modes."""

    _attr_translation_key = "manual_mode"

    @property
    def options(self) -> list[str]:
        """Return all documented mode choices."""
        return [self._mode_option(mode) for mode in MODE_LABELS]

    @property
    def current_option(self) -> str | None:
        """Return the currently reported manual mode."""
        mode = _as_int(self.coordinator.status.get("mode"))
        return self._mode_option(mode) if mode in MODE_LABELS else None

    async def async_select_option(self, option: str) -> None:
        """Set the selected mode and its staged values."""
        mode = next(
            (mode_id for mode_id in MODE_LABELS if self._mode_option(mode_id) == option),
            None,
        )
        if mode is None:
            return
        await self.coordinator.async_select_mode(mode)

    @staticmethod
    def _mode_option(mode: int) -> str:
        return f"{mode} - {MODE_LABELS[mode]}"


class ManualSourceSelect(_AudioPlayerSelect):
    """Stage a source for the source manual modes."""

    _attr_translation_key = "manual_source"

    @property
    def options(self) -> list[str]:
        """Return source names with IDs to disambiguate duplicates."""
        return [self._source_option(source) for source in self.coordinator.sources]

    @property
    def current_option(self) -> str | None:
        """Return the staged or saved manual source."""
        source_id = _as_int(self.coordinator.manual_value("source"))
        for source in self.coordinator.sources:
            if _as_int(source.get("id")) == source_id:
                return self._source_option(source)
        return None

    async def async_select_option(self, option: str) -> None:
        """Stage the source to use when a source mode is selected."""
        selected_source = next(
            (
                source
                for source in self.coordinator.sources
                if self._source_option(source) == option
            ),
            None,
        )
        if selected_source is None:
            return
        source_id = _as_int(selected_source.get("id"))
        if source_id is None:
            return
        self.coordinator.async_stage_manual_value("source", source_id)
        self.async_write_ha_state()

    @staticmethod
    def _source_option(source: dict[str, Any]) -> str:
        return f"{source['name']} ({source['id']})"


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
