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
