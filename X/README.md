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

## Persistent files

- `/data/platform.json` — repositories, applications, token and ENV settings
- `/data/status.json` — runtime state
- `/data/commands.json` — UI-to-manager command queue
- `/data/repositories` — checked out Git repositories
- `/data/logs` — application logs
