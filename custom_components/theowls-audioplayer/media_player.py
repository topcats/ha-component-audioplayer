from __future__ import annotations

from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import AudioPlayerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the media-player entity."""
    coordinator: AudioPlayerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AudioPlayerEntity(coordinator, entry)])


class AudioPlayerEntity(CoordinatorEntity[AudioPlayerCoordinator], MediaPlayerEntity):
    """Represent one TheOwls AudioPlayer instance."""

    _attr_has_entity_name = True
    _attr_name = "Player"
    _attr_media_content_type = MediaType.MUSIC
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(
        self, coordinator: AudioPlayerCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_player"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="TheOwls",
            model="AudioPlayer",
        )

    @property
    def state(self) -> MediaPlayerState:
        """Return the playback state represented by the status payload."""
        mode = self.coordinator.status.get("mode")
        if _as_int(mode) in {1, 2, 3}:
            return MediaPlayerState.OFF
        if (
            self.coordinator.status.get("aPlayer") == "State.Playing"
            or self.coordinator.status.get("aPlayerList") == "State.Playing"
        ):
            return MediaPlayerState.PLAYING
        return MediaPlayerState.IDLE

    @property
    def source(self) -> str | None:
        """Return the name of the current configured source."""
        current_source = self.coordinator.status.get("source")
        if isinstance(current_source, dict):
            name = current_source.get("name")
            return name if isinstance(name, str) else None
        return None

    @property
    def source_list(self) -> list[str]:
        """Return the available source names."""
        return [str(source["name"]) for source in self.coordinator.sources]

    @property
    def media_title(self) -> str | None:
        """Return the current media title or source name."""
        title = self.coordinator.status.get("title")
        if isinstance(title, str) and title:
            return title
        return self.source

    @property
    def media_artist(self) -> str | None:
        """Return the current programme subtitle."""
        subtitle = self.coordinator.status.get("subtitle")
        return subtitle if isinstance(subtitle, str) and subtitle else None

    @property
    def media_image_url(self) -> str | None:
        """Return the current media image, falling back to the source image."""
        image = self.coordinator.status.get("image")
        if isinstance(image, str) and image:
            return image
        current_source = self.coordinator.status.get("source")
        if isinstance(current_source, dict):
            source_image = current_source.get("image")
            return source_image if isinstance(source_image, str) else None
        return None

    @property
    def media_position(self) -> float | None:
        """Return current playback time in seconds when available."""
        return _positive_number(self.coordinator.status.get("playtime"))

    @property
    def media_duration(self) -> float | None:
        """Return media duration in seconds when available."""
        return _positive_number(self.coordinator.status.get("playlength"))

    @property
    def media_position_updated_at(self):
        """Return when the last polled playback position was observed."""
        if self.media_position is None:
            return None
        return dt_util.utcnow()

    async def async_media_play(self) -> None:
        """Start or resume playback through the player API."""
        await self.coordinator.async_player_action("play")

    async def async_media_stop(self) -> None:
        """Stop playback through the player API."""
        await self.coordinator.async_player_action("stop")

    async def async_select_source(self, source: str) -> None:
        """Play the selected configured source in manual mode 12."""
        selected_source = next(
            (item for item in self.coordinator.sources if item.get("name") == source),
            None,
        )
        if selected_source is None:
            return
        source_id = _as_int(selected_source.get("id"))
        if source_id is None:
            return
        self.coordinator.async_stage_manual_value("source", source_id)
        await self.coordinator.async_select_mode(12, source=source_id)


def _as_int(value: Any) -> int | None:
    """Convert an integer-like value without accepting booleans."""
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _positive_number(value: Any) -> float | None:
    """Return a positive numeric value, excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return None
    return float(value)
