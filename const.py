"""Constants for the TheOwls AudioPlayer integration."""

DOMAIN = "theowls-audioplayer"
DEFAULT_NAME = "TheOwls RPI AudioPlayer"
DEFAULT_STATUS_INTERVAL_SECONDS = 60
MIN_STATUS_INTERVAL_SECONDS = 30
MAX_STATUS_INTERVAL_SECONDS = 86400

SYSTEM_PROTOCOL = "http"
SYSTEM_PORT = 8007
SYSTEM_STATUS_PATH = "/status"

CONF_DEVICE_NAME = "device_name"
CONF_STATUS_INTERVAL = "status_interval"

SUPPORTED_PLATFORMS = ["sensor"]


MANUAL_MODE_LABELS = {
    0: "Normal running",
    1: "Full stop; play nothing, schedule paused",
    2: "Stop; play nothing, resume at next schedule change",
    3: "Stop; play nothing, resume at next day",
    11: "Play Source; schedule paused",
    12: "Play Source; resume at next schedule change",
    13: "Play Source; resume at next day",
    21: "Play Url; schedule paused",
    22: "Play Url; resume at next schedule change",
    23: "Play Url; resume at next day",
}
