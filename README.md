# ha-component-audioplayer

HomeAssistant Component TheOwls RPI AudioPlayer Control

## Status sensor

Install this integration in `custom_components/theowls-audioplayer`, then add it
from **Settings > Devices & services > Add integration**. Enter the hostname
only (no scheme, port, or path) and a polling interval in seconds; the default
is 60 seconds. Add the integration again for each additional player, using that
player's hostname. Each hostname creates a separate Home Assistant device, and
the same hostname cannot be added twice. Use an entry's **Configure** action to
change its polling interval later. Remove and re-add an entry to change its
hostname. The endpoint is built as
`http://<host>:8007/status`.

The legacy YAML platform is also supported:

```yaml
sensor:
  - platform: theowls-audioplayer
    host: rpi-2hpdisplay.the-owls.local
    scan_interval: "00:00:30"
```

For YAML, `scan_interval` accepts a Home Assistant time period and defaults to
one minute. The sensor's state uses the JSON `status`, `state`, or `mode` field
when present, and the complete JSON object is available as state attributes.
