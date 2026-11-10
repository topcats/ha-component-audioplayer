from __future__ import annotations

from curses import error
import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AudioPlayerApi, AudioPlayerApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AudioPlayerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure a TheOwls AudioPlayer instance."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up a player by host."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip().strip("[]").rstrip(".")
            _LOGGER.debug("TheOwls-AudioPlayer: Setup Configuring AudioPlayer %s", host)
            if not host or "://" in host or "/" in host:
                errors["base"] = "invalid_host"
            else:
                api = AudioPlayerApi(async_get_clientsession(self.hass), host)
                try:
                    # Test connection to the player
                    await api.async_get_status()
                    # Check That is a valid system by checking for the webapi key in the config
                    config = await api.async_get_config()
                    if config is None or 'webapi' not in config:
                        errors["base"] = "invalid_response"
                except Exception as error:
                    _LOGGER.error("TheOwls-AudioPlayer: Setup Error connecting to AudioPlayer %s. %s", host, error)
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(host.lower())
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=api.name,
                        data=user_input,
                    )

        schema = vol.Schema(
            {vol.Required(CONF_HOST): cv.string}
        )
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )
