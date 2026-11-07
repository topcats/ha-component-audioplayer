import asyncio
from importlib import import_module

import pytest

audio_player_api = import_module("custom_components.theowls-audioplayer.api")
AudioPlayerApi = audio_player_api.AudioPlayerApi
AudioPlayerApiError = audio_player_api.AudioPlayerApiError
build_control_payload = audio_player_api.build_control_payload


@pytest.mark.parametrize(
    ("mode", "source", "url", "title", "image", "expected"),
    [
        (0, 5, "https://example.test/live", "Radio", "https://example.test/a.jpg", {
            "mode": 0,
            "source": None,
            "url": None,
            "title": None,
            "image": None,
        }),
        (1, 5, "https://example.test/live", "Radio", "https://example.test/a.jpg", {
            "mode": 1,
            "source": None,
            "url": None,
            "title": None,
            "image": None,
        }),
        (2, 5, "https://example.test/live", "Radio", "https://example.test/a.jpg", {
            "mode": 2,
            "source": None,
            "url": None,
            "title": None,
            "image": None,
        }),
        (3, 5, "https://example.test/live", "Radio", "https://example.test/a.jpg", {
            "mode": 3,
            "source": None,
            "url": None,
            "title": None,
            "image": None,
        }),
        (11, 5, "https://example.test/live", "Radio", "https://example.test/a.jpg", {
            "mode": 11,
            "source": 5,
            "url": None,
            "title": None,
            "image": None,
        }),
        (12, 5, None, None, None, {
            "mode": 12,
            "source": 5,
            "url": None,
            "title": None,
            "image": None,
        }),
        (13, 5, None, None, None, {
            "mode": 13,
            "source": 5,
            "url": None,
            "title": None,
            "image": None,
        }),
        (21, None, "https://example.test/live", "Radio", "https://example.test/a.jpg", {
            "mode": 21,
            "source": None,
            "url": "https://example.test/live",
            "title": "Radio",
            "image": "https://example.test/a.jpg",
        }),
        (22, None, "https://example.test/live", "Radio", "https://example.test/a.jpg", {
            "mode": 22,
            "source": None,
            "url": "https://example.test/live",
            "title": "Radio",
            "image": "https://example.test/a.jpg",
        }),
        (23, None, "https://example.test/live", "Radio", "https://example.test/a.jpg", {
            "mode": 23,
            "source": None,
            "url": "https://example.test/live",
            "title": "Radio",
            "image": "https://example.test/a.jpg",
        }),
    ],
)
def test_build_control_payload(mode, source, url, title, image, expected):
    assert build_control_payload(mode, source, url, title, image) == expected


class FakeResponse:
    def __init__(self, data):
        self.data = data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    def raise_for_status(self):
        return None

    async def json(self, content_type=None):
        return self.data


class FakeSession:
    def __init__(self, data):
        self.data = data
        self.requests = []

    def request(self, method, url, **kwargs):
        self.requests.append((method, url, kwargs))
        return FakeResponse(self.data)


def test_set_mode_sends_put_control_payload():
    session = FakeSession({"action": True, "return": True})
    api = AudioPlayerApi(session, "player.local")

    asyncio.run(api.async_set_mode(12, source=5))

    method, url, kwargs = session.requests[0]
    assert method == "PUT"
    assert url == "http://player.local:8007/control"
    assert kwargs["json"] == {
        "mode": 12,
        "source": 5,
        "url": None,
        "title": None,
        "image": None,
    }


def test_set_url_mode_sends_url_metadata():
    session = FakeSession({"action": True, "return": True})
    api = AudioPlayerApi(session, "player.local")

    asyncio.run(
        api.async_set_mode(
            22,
            url="https://example.test/live",
            title="Radio",
            image="https://example.test/a.jpg",
        )
    )

    method, url, kwargs = session.requests[0]
    assert method == "PUT"
    assert url == "http://player.local:8007/control"
    assert kwargs["json"] == {
        "mode": 22,
        "source": None,
        "url": "https://example.test/live",
        "title": "Radio",
        "image": "https://example.test/a.jpg",
    }


def test_player_action_rejects_unsuccessful_response():
    session = FakeSession({"return": False})
    api = AudioPlayerApi(session, "player.local")

    with pytest.raises(AudioPlayerApiError):
        asyncio.run(api.async_player_action("play"))
