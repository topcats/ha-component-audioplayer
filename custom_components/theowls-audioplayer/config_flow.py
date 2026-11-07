from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AudioPlayerApi, AudioPlayerApiError
from .const import DOMAIN


class AudioPlayerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a TheOwls AudioPlayer instance."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up a player by host."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip().strip("[]").rstrip(".")
            if not host or "://" in host or "/" in host:
                errors["base"] = "invalid_host"
            else:
                api = AudioPlayerApi(async_get_clientsession(self.hass), host)
                try:
                    await api.async_get_status()
                    config = await api.async_get_config()
                    if not isinstance(config.get("sources"), list):
                        errors["base"] = "invalid_response"
                except AudioPlayerApiError:
                    errors["base"] = "cannot_connect"

                if not errors:
                    await self.async_set_unique_id(host.lower())
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=host,
                        data={CONF_HOST: host},
                    )

        schema = vol.Schema(
            {vol.Required(CONF_HOST): cv.string}
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
