# X Platform

X Platform is a new combined Home Assistant add-on built alongside the existing
`node_server`, `node_server_ui`, `popcorn`, `x_installer`, and `plugins`
directories. Those existing add-ons are not modified or removed.

## Included features

- Scrypted-style launcher for the Console and installed web applications.
- Built-in plugin catalog with Popcorn as the first official plugin.
- Public and private GitHub repository discovery.
- Multiple GitHub accounts through PAT credentials or GitHub Device Login.
- Repository scanning for multiple applications and integrations.
- Per-repository environment variables stored in the add-on's persistent
  `/data/platform.json` file with mode `0600`.
- Per-application port, install, build, and start configuration.
- Direct LAN URLs on the Home Assistant host, for example
  `http://10.0.0.2:5173`, using `host_network` and a configurable LAN host/IP.
- Process start, stop, restart, update, status, and logs.
- Built-in X Installer that copies compatible integrations to
  `/homeassistant/custom_components`.
- Entity integration recommendation when a plugin declares discovery support or
  recognizable Extaas entity code is detected.

## Plugin convention

Custom repositories can be configured directly from the UI. For a future
catalog entry, the equivalent metadata is:

```json
{
  "id": "example",
  "name": "Example",
  "repository": "owner/repository",
  "pluginPath": ".",
  "port": 8090,
  "install": "npm ci",
  "build": "npm run build",
  "start": "node build/index.js",
  "homeAssistant": { "discovery": true }
}
```

Applications must listen on `process.env.PORT` to honor the selected port. The
manager also sets `HOST=0.0.0.0`, which exposes the application on the Home
Assistant host's LAN address.

### Build completion and timeout behavior

X runs the configured Build command before the Start command. A build that
exits normally continues immediately to Start. Some build tools finish their
work but keep the process open, so X also treats 180 seconds without new build
output as completion: the idle build process is stopped and the Start command
is launched. Every stdout or stderr entry resets the 180-second timer. A
separate 15-minute maximum build timeout remains in place for builds that keep
producing output indefinitely. Non-zero build exits remain errors and do not
start the application.

## Repository metadata (`x_config.json`)

One repository may contain multiple applications. Put an `x_config.json` at
the repository root (or in a discoverable subdirectory):

```json
{
  "applications": [
    {
      "id": "popcorn",
      "name": "Popcorn",
      "path": "popcorn",
      "icon": "applications/popcorn/icon.png",
      "background": "applications/popcorn/background.webp",
      "port": 5173,
      "install": "npm ci",
      "build": "npm run build",
      "start": "node build/index.js",
      "homeAssistant": { "discovery": true }
    }
  ]
}
```

`icon` and `background` are repository-relative image paths. Supported formats
are PNG, JPEG, WebP, GIF and SVG. X Platform serves them read-only and prevents
paths from leaving the checked-out repository.

Home Assistant integrations are detected from compatible `manifest.json`
files. Installed integration source is archived under `/data/integrations`
before being copied to `custom_components`, so removal from the source repo
does not automatically remove the installed integration.

## Direct Home Assistant API

Managed applications run as child processes of the X add-on. Home Assistant
provides `SUPERVISOR_TOKEN` to the add-on at runtime and the child processes
inherit it; X does not store it in application or repository ENV settings.
Use Home Assistant's documented internal Core API URL directly:

```js
const response = await fetch('http://supervisor/core/api/services/light/turn_on', {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${process.env.SUPERVISOR_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ entity_id: 'light.living_room' })
});
```

The same API provides `/states`, entity data, lights, switches, scripts,
service calls, notifications, and the other capabilities allowed by
`homeassistant_api: true`. User-editable application and repository ENV
settings are intended for application-specific secrets such as TMDB or
Discord credentials. Because custom applications inherit the Home Assistant
runtime token, only trusted repositories should be installed.

## Publishing application entities

Each application owns its Home Assistant device and entity definitions. X only
injects `X_APPLICATION_ID`, `X_ENTITIES_HUB_HOST`, and `X_ENTITIES_HUB_PORT` so
the application can attach its payload to the existing X Platform config entry.
The application discovers Home Assistant and posts directly to X Entities:

```js
async function sendEntities(haUrl, host, port, nodeData) {
  await fetch(`${haUrl}/api/extaas_com`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      host,
      port,
      hub_host: process.env.X_ENTITIES_HUB_HOST,
      hub_port: Number(process.env.X_ENTITIES_HUB_PORT),
      source_id: process.env.X_APPLICATION_ID,
      node_data: nodeData
    })
  });
}
```

The application exposes `POST /update` on its own port. X Entities sends switch
and button changes directly there using the original entity key. `source_id`
isolates each application's snapshot, so one application cannot delete another
application's entities. X Entities automatically connects the application device
to the X Platform hub. X does not receive or manage application entity data.
Application start and stop remain internal X Console actions and are not exposed
as X Entities entities.

Applications should publish at least every 20 seconds (the recommended interval
is 5 seconds). If a source stops publishing, its entities become unavailable
after 20 seconds. After 90 seconds X Entities removes that source's entities and
its now-empty application device automatically.

Use a `heartbeat`, `alive`, or `online` entity (or `device_class: connectivity`)
with `type: binary_sensor` and `value: true`. If publishing stops, X Entities
changes that heartbeat to `false`; unlike the source's other entities, the
heartbeat remains available until the application device is removed.

## Persistent files

- `/data/platform.json` — repositories, applications, token and ENV settings
- `/data/status.json` — runtime state
- `/data/commands.json` — UI-to-manager command queue
- `/data/repositories` — checked out Git repositories
- `/data/logs` — application logs
