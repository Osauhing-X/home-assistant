# Changelog

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
