# Home Assistant Entities API

Package identity: home-assistant-entities; Core integration ID: io.extaas.home-assistant-entities. Required host: home-assistant. The package contains native HA Python code; it declares no callable Node/Core gateway actions and is not an arbitrary HA API proxy.

## Workspace Core connectivity

The workspace-core setup flow reads GET http://<configured-host>:<port>/health and accepts only HTTP 200 JSON with ok: true and service: workspace-core. Redirects are refused; bodies are limited to 4096 bytes. This public health check does not grant administrator access or reveal package/customer records.

## Compatible legacy entity publishers

POST /api/extaas_com is registered inside Home Assistant by custom_components/extaas_com/api.py. It requires normal Home Assistant API authentication. A publisher must match an existing configured hub entry and send the instance-owned source/node data contract; unknown entries are rejected. Core-mode entries provide a connectivity sensor only, so publishing legacy entity payloads is not a claim that Core command/update routes exist. The retired X manager's /api/integrations/update and unauthenticated /update bridge are not installed by the new add-on.

Never put a Supervisor token in a package manifest or browser UI. The Workspace add-on does not receive HA API grants and strips Supervisor control credentials before starting Core. Native integration installation/reload is performed through Home Assistant, not by declaring this metadata.
