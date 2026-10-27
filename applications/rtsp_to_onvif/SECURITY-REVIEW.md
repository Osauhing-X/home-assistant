# RTSP source review — 27 October 2026

This receipt covers version 0.8.4 source preparation. It does not certify the
entire application as production-ready or complete the requested standalone addon.

## Implemented and checked

- Anonymous `/snapshot/<camera-id>.jpg` requests return 401 and do not start
  FFmpeg. A real curl HTTP Digest client retrieved a synthetic JPEG through the
  handler. Camera username/password and request URI are checked; signed nonces
  expire after five minutes and accepted nonce counts cannot be replayed.
- Snapshot URLs remain stable, with `PT0S` in both media endpoints, following
  [ONVIF Media snapshot URI requirements](https://www.onvif.org/specs/srv/media/ONVIF-Media-Service-Spec-v1806.pdf).
  Digest uses the camera's configured ONVIF credentials as required for HTTP
  media access by the [ONVIF Core specification](https://www.onvif.org/specs/core/ONVIF-Core-Specification.pdf).
  MD5 compatibility is retained for RFC 2617 clients. These checks do not add TLS.
- A configured GUI session can request a snapshot. An unset GUI password never
  authenticates, including with the former predictable empty-password hash.
- GUI cookies use signed, random session identities with a seven-day expiry
  enforced on the server. Password changes invalidate previous signatures. Old
  static password-hash cookies are rejected; upgrading requires signing in again.
- Snapshot limits: four simultaneous workers, ten-second timeout and 8 MiB JPEG
  output. Failed/cancelled/oversized workers are stopped. Errors are generic;
  source credentials are not returned. Output must have JPEG boundaries.
- Camera/settings reads distinguish a missing file from corrupt JSON, invalid
  structure or filesystem failure. Failed reads cannot overwrite the original.
  Camera API changes, DHCP updates and discovery expiry include the read inside
  a per-file transaction. Twenty concurrent updates retained all records.
- New configuration files use private atomic replacement and fsync. Unix
  directories/files use 0700/0600. Windows ACLs are not managed by these mode bits.
  Camera and relay configuration still contain source credentials; they are not
  encrypted at rest. One application process must own the data directory.
- The GUI reports unavailable storage instead of claiming there are no cameras.
  A synthetic corrupted file was repaired and the UI recovered with Try again.
  Failed camera saves retain the editor. The list hides URI credentials/query
  tokens; explicit editing remains available to the authenticated administrator.
- Native modal focus, Tab wrapping, Escape close and focus restoration were
  checked in a browser. Camera and settings dialogs had no Axe WCAG A/AA
  violations or incomplete checks in the tested desktop/mobile states. The
  mobile camera dialog had no horizontal overflow. This is component evidence,
  not a complete accessibility audit of the final addon.
- Built HTTP checks verified anonymous management denial, cross-origin mutation
  denial, a safe login return path, HTTP-only login cookie, nonempty camera
  credentials and authenticated snapshot URI responses. Tests used temporary
  synthetic storage with hardware services disabled.
- Both generic and camera-specific media endpoints return relay stream URIs,
  not the physical source URI/credentials. ffprobe failures are generic and
  diagnostic targets omit source paths and authentication fields.

Run `npm ci`, `npm run build`, then `npm test`. The GitHub workflow repeats these
checks and rejects high/critical npm findings.

## Dependency state

Compatible updates removed the three high-risk findings in the initial install.
`cookie` is overridden to a patched compatible 0.7 release. npm still reports two
low-risk SvelteKit advisories through Kit/adapter-node:

- [GHSA-pfhg-q3qv-9q6r](https://github.com/advisories/GHSA-pfhg-q3qv-9q6r):
  double-slash paths are rejected in the hook, matching the documented workaround.
- [GHSA-27mw-82g8-phjj](https://github.com/advisories/GHSA-27mw-82g8-phjj):
  management pages explicitly disable prerendering and do not forward untrusted
  cache-control values into prerendered HTML.

These mitigations do not remove the packages from the advisory's version range.
Kit 3.1 requires Node >=22.17 and newer peers; the checked local runtime is
22.12. The standalone image/runtime/framework migration is still required.

## Required before standalone rollout

1. Verify the new exact-path RTSP read permissions with a real recorder.
   A loopback MediaMTX 1.19.3 acceptance test confirms anonymous/wrong-password
   and cross-camera requests receive 401; authorized empty HQ/LQ paths receive
   404 because no publisher exists. Generated configuration replaces anonymous defaults with
   camera credentials and read-only HQ/LQ permissions. Empty credentials, reserved
   `any` users and conflicting paths fail closed. Two configuration tests and
   the real MediaMTX authorization test pass; media/recorder compatibility is untested.
2. Replace or authenticate the legacy X `/update` bridge. It remains an exception
   to browser session/origin checks for compatibility, not a secure public API.
3. Review WS-Security timestamp/replay handling, blank legacy credentials and
   GUI login rate limits. Bound preview/probe
   workers as well; the new snapshot worker pool does not govern those paths.
4. Add Extaas Connect account linking, paid access checks and a safe migration of
   existing paid rights. A test billing ledger must never unlock production.
5. Package the separate addon, preserve `/data/application-data/rtsp-to-onvif`,
   improve the complete Extaas UI and verify an actual camera/NVR/HA installation.

No real camera, LAN discovery, network alias, Home Assistant service
or production deployment was operated during these acceptance tests. Existing
uncommitted X Platform work on the E drive was inspected by filename and retained;
this review uses a separate C-drive clone.
