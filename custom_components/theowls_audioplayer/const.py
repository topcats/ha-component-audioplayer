from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "theowls-audioplayer"
PLATFORMS = (Platform.MEDIA_PLAYER, Platform.SELECT, Platform.TEXT)

PORT = 8007
UPDATE_INTERVAL = timedelta(seconds=60)
REQUEST_TIMEOUT = 10

SOURCE_MODES = frozenset({11, 12, 13})
URL_MODES = frozenset({21, 22, 23})
STOP_MODES = frozenset({1, 2, 3})

MODE_LABELS = {
    0: "Normal running",
    1: "Full stop",
    2: "Stop, resume next schedule",
    3: "Stop, resume next day",
    11: "Play source, schedule paused",
    12: "Play source, resume next schedule",
    13: "Play source, resume next day",
    21: "Play URL, schedule paused",
    22: "Play URL, resume next schedule",
    23: "Play URL, resume next day",
}

MANUAL_OPTION_KEYS = {
    "source": "manual_source",
    "url": "manual_url",
    "title": "manual_title",
    "image": "manual_image",
}
