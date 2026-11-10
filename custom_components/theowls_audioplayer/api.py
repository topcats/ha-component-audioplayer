from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
from yarl import URL

from .const import PORT, REQUEST_TIMEOUT, SOURCE_MODES, URL_MODES


class AudioPlayerApiError(Exception):
    """Raised when the AudioPlayer API cannot complete a request."""


def build_control_payload(
    mode: int,
    source: int | str | None = None,
    url: str | None = None,
    title: str | None = None,
    image: str | None = None,
) -> dict[str, int | str | None]:
    """Build the control request, nulling fields unused by the selected mode."""
    return {
        "mode": mode,
        "source": source if mode in SOURCE_MODES else None,
        "url": url if mode in URL_MODES else None,
        "title": title if mode in URL_MODES else None,
        "image": image if mode in URL_MODES else None,
    }


class AudioPlayerApi:
    """Async client for the TheOwls AudioPlayer HTTP API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
    ) -> None:
        self._session = session
        # Build a base URL for the player
        normalized_host = host.strip().strip("[]")
        if ":" in normalized_host:
            normalized_host = f"[{normalized_host}]"
        self._base_url = f"http://{normalized_host}:{PORT}"
        # Save Host Name
        self._host_name = host.strip().strip("[]").split('.')[0].upper()

    @property
    def name(self) -> str | None:
        """Return the name of the current configured host."""
        return self._host_name if hasattr(self, "_host_name") else None


    async def async_get_status(self) -> dict[str, Any]:
        """Return the current player status."""
        return await self._async_request("GET", "/status")

    async def async_get_config(self) -> dict[str, Any]:
        """Return player configuration, including available sources."""
        return await self._async_request("GET", "/config")

    async def async_player_action(self, action: str) -> None:
        """Call a direct player action such as play or stop."""
        result = await self._async_request("GET", f"/player/{action}")
        if result.get("return") is not True:
            raise AudioPlayerApiError(f"Player action {action} was rejected")

    async def async_set_mode(
        self,
        mode: int,
        source: int | str | None = None,
        url: str | None = None,
        title: str | None = None,
        image: str | None = None,
    ) -> None:
        """Set a manual mode and its mode-specific values."""
        payload = build_control_payload(mode, source, url, title, image)
        result = await self._async_request("PUT", "/control", json_body=payload)
        if result.get("action") is not True:
            message = result.get("message", "Manual mode change was rejected")
            raise AudioPlayerApiError(str(message))

    async def _async_request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a request and require a JSON object response."""
        url = str(URL(self._base_url).join(URL(path)))
        try:
            async with self._session.request(
                method,
                url,
                json=json_body,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as response:
                response.raise_for_status()
                result = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise AudioPlayerApiError(f"Request to {path} failed: {err}") from err

        if not isinstance(result, dict):
            raise AudioPlayerApiError(f"Invalid JSON response from {path}")
        return result
