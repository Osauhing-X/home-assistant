# Changelog

## 1.0.0 — 2026-10-29

- Replace the separate X Platform manager with the shared Workspace Core add-on.
- Preserve Core data under Supervisor /data and expose its authenticated web UI on a configurable mapped port.
- Do not grant Docker, Supervisor control, host-network or HA configuration access.
- Support amd64/aarch64 only; ingress and automatic legacy registry conversion are not claimed.
