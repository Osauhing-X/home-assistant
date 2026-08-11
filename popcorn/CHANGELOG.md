# Changelog

All notable changes to Popcorn by Osaühing X are documented here.

---

## Version 3.2.0 — 2026-08-11

### Added

- Expandable folder movie lists plus folder-wide and individual Home Assistant entity toggles.
- Saved-list name/folder search, datalist suggestions and five practical sorting modes.
- GitHub-style yearly calendar with month filtering for personal and family lists.
- Saved Estonian/English portal language preference and catalog navigation in the landing header.

### Changed

- Saved cards now open movie details and `/favorite` leads to the unified “Me & family” workflow.
- Detail saving now uses personal, family and folder storage instead of legacy favorites/date controls.
- Redesigned providers, personal links, catalog filters and pagination for the premium Popcorn design system.

### Fixed

- Improved date filtering, responsive saved cards and expanded-folder overflow behavior.
- Added safe allowlisting for individual and folder-wide Home Assistant toggles.

---

## Version 3.1.0 — 2026-08-11

### Fixed

- Fixed the minified `Oa is not a function` runtime crash in personal, family and folder views by rendering Svelte snippets correctly.
- Fixed broken local-link translation access and undefined link-list iteration on detail pages.
- Fixed ingress-aware redirects and links across movie routes.
- Added portal-wide overflow protection for narrow Home Assistant panels and mobile screens.
- Removed the oversized search popover zoom that caused viewport overflow.

### Changed

- Rebuilt movie search, favorites and detail routes with the same premium design system as the landing page.
- Added a shared responsive portal header and consistent navigation.
- Rebuilt poster and grid components with stable responsive sizing and native lazy loading.
- Added the supplied Osaühing X logo to navigation and the support panel.
- Redesigned detail heroes, metadata, actions and expandable content sections.

---

## Version 3.0.1 — 2026-08-11

### Fixed

- Fixed the server-side `ReferenceError: Cannot access 'image' before initialization` that caused the Popcorn ingress root page to return HTTP 500.
- Made the poster URL helper safe during Svelte server-side initialization.

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
