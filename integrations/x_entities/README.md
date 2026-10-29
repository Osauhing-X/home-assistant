# Home Assistant Entities

This is a native Home Assistant integration, not a second Workspace manager. The root Workspace manifest declares platforms: ["home-assistant"]. Core must reject installation/activation on other hosts.

Copy **custom_components/extaas_com** into your Home Assistant configuration's custom_components directory and restart Home Assistant. The inner manifest.json is the native HA manifest; the package-root manifest.json belongs to Workspace. Do not copy the root manifest into the native component directory.

Add **Workspace Entities** in Home Assistant and choose workspace-core. Enter your HA host/LAN address and Workspace's mapped port (default 3010). Setup checks the exact Workspace /health response without redirects. The integration creates a read-only connectivity sensor. It does not expose Core administrator sessions, install packages or use the retired X update API. Legacy node entries retain their existing protocol; the stable HA domain extaas_com and stored entity IDs are retained.

Dynamic entity publishing to /api/extaas_com now requires normal Home Assistant API authentication. Old anonymous publisher examples are retired. Application entity/action migration and live HA/Supervisor acceptance remain separate checks; this package does not claim complete old X bridge parity.
