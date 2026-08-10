# Changelog

All notable changes to Popcorn by Osaühing X are documented here.

---

## Version 3.0.0 — 2026-08-10

### Added

- Personal watchlists stored locally in each browser.
- Shared family watchlists persisted in the add-on `/data` directory.
- Family folders with members, rooms and folder-specific notification recipients.
- Automatic discovery of Home Assistant `person.*`, `light.*`, `switch.*` and `notify.*` entities and services.
- Home Assistant persistent notifications when dated family items are saved.
- Background reminder worker that sends notifications when a saved date arrives.
- Movie-night controls for turning off each folder's selected lights and switches.
- Popcorn notification settings for default family recipients.
- Support panel with Osaühing X support and Extaas contact links.

### Changed

- Rebuilt the home experience with a modern responsive premium interface.
- Redesigned discovery, search, saved items, folders and settings views.
- Removed external font loading so the interface remains available locally.
- Added clear Osaühing X product attribution throughout the interface and metadata.
- Updated the add-on description to reflect local-first Home Assistant integration.

### Notes

- Movie metadata and artwork still use the configured TMDB API.
- Plex integration is not included in this release.
