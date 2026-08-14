# Changelog

## 1.0.1

- Added direct application-owned X Entities publishing for Popcorn and RTSP to
  ONVIF, including heartbeat and read-only health entities.
- Added privacy-safe aggregate RTSP camera connectivity notifications.
- Added source timeout handling and binary sensor support to X Entities.
- Fixed the add-on Supervisor architecture identifier from `amd64s` to `amd64`.

## 0.6.0

- Separated build and start again with a generic 180-second build-output idle
  fallback, so tools that finish work but keep their process open cannot block
  the application queue indefinitely.
- Changed managed application updates to a single tracked
  `build && start` process; the queue is released after spawning and runtime
  state switches from updating to running when the server reports readiness.
- Added bounded install/build execution and phase-by-phase reload logging, and
  stopped application-only version bumps from triggering a full `npm ci`.
- Fixed concurrent status writes during application reloads by assigning every
  atomic write its own temporary file.
- Fixed reload-code tasks hanging after successful builds by waiting for the
  previous process to exit and containing task failures inside the manager.
- Renamed Dashboard health panels to overview panels and added repository
  detected totals plus last-scanned timestamps.
- Removed the redundant Integrations `Update all` action; repository scans now
  only stage updates and Home Assistant remains the install/skip authority.
- Added the LAN-facing runtime `ORIGIN` for managed SvelteKit applications so
  password and other same-origin POST forms pass CSRF validation.
- Moved application and integration delete actions into their Overview tabs,
  added application status colors, and made launcher choices health-aware.
- Stopped GUI applications are hidden from the launcher; failed applications
  remain visible but disabled, while install/update tasks retain loading rows.
- Fixed X Entities dispatcher callbacks so staged integration updates and
  application devices are created when bridge data arrives after HA startup.
- Fixed repository defaults overriding an application's configured runtime
  port and commands when the manager starts or updates it.
- Removed the duplicate application status badge from the controls and added
  semantic status colors to the Overview card.

## 0.5.9

- Fixed application update tasks remaining in the updating state after builds.
- Reused unchanged `node_modules` during code reloads and switched Popcorn's
  clean install to the faster reproducible `npm ci` flow.
- Forced manual Git scans to match the fetched remote commit and derive staged
  integration versions from the copied manifest.
- Added application deletion, complete merged ENV schemas, and tabbed
  integration details with overview, logs, and documentation.
- Removed Home Assistant application entities and devices when their X
  application is deleted.

## 0.5.8

- Integration update indicators now follow the version physically staged in
  each integration's `new_version` directory.
- Installing an integration update consumes the staged copy and clears the
  available-version marker.
- Skipping an update in Home Assistant removes its staged copy and keeps that
  exact version ignored until a newer release is found.

## 0.5.6

- Added a live Queued view with active and pending manager tasks.
- Queue tasks now remain visible until the underlying install, build, reload,
  start, repository scan, or integration operation has actually completed.
- Added real-time application status and terminal log updates with cache-free
  polling, so completed operations disappear without a page refresh.
- Added repository-wide `Scan / Git pull all`, scan timestamps, and per-source
  application plus integration update counts.
- Unified application and integration version columns into the compact
  `installed -> available` format.
- Added staged application code copies, manual reload/update indicators, and
  version-aware automatic update checks.
- Added application devices to X Entities with status sensors, start/stop
  switches, and Home Assistant Visit links for GUI applications.
- Renamed the bundled Home Assistant integration to X Entities and improved
  update discovery for Home Assistant's Updates dashboard.
- Added schema-driven application environment fields and optional application
  password protection.
- Improved the application launcher, logos, loading states, navigation, mobile
  menu, repository details, application overview, and terminal controls.
- Updated Popcorn for the X application runtime with optional reminders,
  background due-date notifications, favicon, title, and link naming.

## 0.3.0

- Managed applications inherit Home Assistant's runtime `SUPERVISOR_TOKEN` and
  use the documented `http://supervisor/core/api` endpoint directly; X no
  longer injects custom Home Assistant URL or bridge variables.
- Added scheduled update detection, Dashboard update notices, staged Home
  Assistant integration updates, and application update policies.
- Added integration path and last-change columns plus expanded details.
- Added searchable portal/application/integration/repository activity logs.

## 0.2.0

- Added multiple GitHub accounts and OAuth Device Login.
- Added multi-application and multi-integration repository scanning.
- Added minimalist catalog/repository tables and detail routes.
- Added persistent managed integration archives and version management.
- Added Home Assistant notifications, discovery and platform/application entities.
- Added reactive sidebar navigation, Dashboard and Discord-style Discover view.
- Added direct public repository entry without authentication.
- Simplified account setup to GitHub OAuth and added notification preferences.
- Applied the Osaühing X `#da3` brand color and state-aware application actions.
- Combined GitHub OAuth setup and connected accounts into one Settings section.
- Added Home Assistant notification recipients using persistent notifications and discovered `notify.*` services.
- Removed the Discover hero banner for a cleaner catalog-first layout.

## 0.1.0

- Initial combined X Platform add-on.
- Added plugin launcher, process manager, GitHub repositories and ENV storage.
- Added Popcorn catalog entry and built-in X Installer compatibility.
