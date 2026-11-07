from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import AudioPlayerApi, AudioPlayerApiError
from .const import (
    DOMAIN,
    MANUAL_OPTION_KEYS,
    SOURCE_MODES,
    UPDATE_INTERVAL,
    URL_MODES,
)


class AudioPlayerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll status and configuration for one AudioPlayer instance."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: AudioPlayerApi,
    ) -> None:
        self.config_entry = entry
        self.api = api
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch status and source configuration together."""
        try:
            status, config = await asyncio.gather(
                self.api.async_get_status(), self.api.async_get_config()
            )
        except AudioPlayerApiError as err:
            raise UpdateFailed(str(err)) from err

        sources = config.get("sources")
        if not isinstance(sources, list):
            raise UpdateFailed("The player configuration has no valid sources list")
        return {"status": status, "config": config}

    @property
    def status(self) -> dict[str, Any]:
        """Return the latest status payload."""
        return self.data["status"]

    @property
    def config(self) -> dict[str, Any]:
        """Return the latest player configuration."""
        return self.data["config"]

    @property
    def sources(self) -> list[dict[str, Any]]:
        """Return configured sources with valid identifiers and names."""
        return [
            source
            for source in self.config.get("sources", [])
            if isinstance(source, dict)
            and source.get("id") is not None
            and source.get("name")
        ]

    def manual_value(self, key: str) -> Any:
        """Return a staged value or the value currently saved by the player."""
        option_key = MANUAL_OPTION_KEYS[key]
        if option_key in self.config_entry.options:
            return self.config_entry.options[option_key]
        manual = self.config.get("manual", {})
        if not isinstance(manual, dict):
            return None
        return manual.get(key)

    def async_stage_manual_value(self, key: str, value: str | int) -> None:
        """Persist a pending manual input in this config entry's options."""
        options = dict(self.config_entry.options)
        options[MANUAL_OPTION_KEYS[key]] = value
        self.hass.config_entries.async_update_entry(self.config_entry, options=options)

    async def async_select_mode(self, mode: int, source: int | str | None = None) -> None:
        """Send the selected mode with the values required by that mode."""
        source_value: int | str | None = None
        url_value: str | None = None
        title_value: str | None = None
        image_value: str | None = None

        if mode in SOURCE_MODES:
            source_value = source if source is not None else self.manual_value("source")
            if source_value in (None, ""):
                raise HomeAssistantError("Choose a source before selecting this mode")
            try:
                source_value = int(source_value)
            except (TypeError, ValueError) as err:
                raise HomeAssistantError("The selected source ID is invalid") from err

        if mode in URL_MODES:
            url_value = self.manual_value("url")
            if not isinstance(url_value, str) or not url_value.strip():
                raise HomeAssistantError("Enter a URL before selecting this mode")
            title = self.manual_value("title")
            image = self.manual_value("image")
            title_value = title if isinstance(title, str) and title else None
            image_value = image if isinstance(image, str) and image else None

        await self.api.async_set_mode(
            mode,
            source=source_value,
            url=url_value,
            title=title_value,
            image=image_value,
        )
        await self.async_request_refresh()

    async def async_player_action(self, action: str) -> None:
        """Run a direct player action and refresh state."""
        await self.api.async_player_action(action)
        await self.async_request_refresh()
