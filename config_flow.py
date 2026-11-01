from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_STATUS_INTERVAL_SECONDS,
    MIN_STATUS_INTERVAL_SECONDS,
    MAX_STATUS_INTERVAL_SECONDS,
)


def _config_schema(
    defaults: dict[str, object] | None = None, *, include_host: bool = True
) -> vol.Schema:
    """Build the setup/options form schema."""
    defaults = defaults or {}
    schema: dict[vol.Marker, object] = {
        vol.Required(
            CONF_SCAN_INTERVAL,
            default=defaults.get(
                CONF_SCAN_INTERVAL, DEFAULT_STATUS_INTERVAL_SECONDS
            ),
        ): vol.All(
            vol.Coerce(int),
            vol.Range(
                min=MIN_STATUS_INTERVAL_SECONDS,
                max=MAX_STATUS_INTERVAL_SECONDS,
            ),
        ),
    }
    if include_host:
        schema[
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, ""))
        ] = vol.All(cv.string, str.strip, vol.Length(min=1))
    return vol.Schema(schema)


class TheOwlsAudioPlayerConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Handle setup of TheOwls AudioPlayer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, object] | None = None
    ) -> config_entries.FlowResult:
        """Show the initial configuration form."""
        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip().lower()
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=host,
                data={**user_input, CONF_HOST: host},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_config_schema(),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> TheOwlsAudioPlayerOptionsFlow:
        """Return the options flow for an existing entry."""
        return TheOwlsAudioPlayerOptionsFlow(config_entry)


class TheOwlsAudioPlayerOptionsFlow(config_entries.OptionsFlow):
    """Handle AudioPlayer option changes."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, object] | None = None
    ) -> config_entries.FlowResult:
        """Show and save the options form."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_config_schema(
                {**self.config_entry.data, **self.config_entry.options},
                include_host=False,
            ),
        )
