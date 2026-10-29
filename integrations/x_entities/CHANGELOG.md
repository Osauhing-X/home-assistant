# Changelog

## 3.0.0 — 2026-10-29

- Separate the Workspace package manifest from the native HA component manifest; require the home-assistant host platform.
- Add verified, bounded read-only Workspace Core connectivity setup and sensor.
- Preserve the native extaas_com domain and legacy entry protocol; do not advertise retired X manager controls for Core connections.
- Require HA API authentication for dynamic entity publishing and stop logging request payloads.
