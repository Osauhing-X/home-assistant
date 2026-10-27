# Changelog

## 0.8.4 — 2026-10-27

- Restrict relay reads to exact camera HQ/LQ paths using camera credentials;
  remove anonymous/default publishing permissions. Validate authorization with
  MediaMTX 1.19.3 on loopback without connecting to a camera.
- Protect JPEG snapshot requests with the configured camera's ONVIF HTTP Digest
  credentials or an existing authenticated GUI session. Keep the snapshot URI
  stable; reject replayed requests and expired challenges before starting FFmpeg.
- Use the same relay URI response for generic and camera-specific ONVIF media
  endpoints instead of exposing the physical camera URI from the generic route.
  Do not log ffprobe errors containing source credentials.
- Bound snapshot worker count, output size and time; do not return FFmpeg source
  errors. Redact URI-bearing relay diagnostics and write private configuration
  with atomic replacement and Unix 0700/0600 permissions.
- Refuse to read or replace corrupt camera/settings files as empty defaults.
  Serialize camera API, DHCP and discovery-expiry read-modify-write updates.
- Show storage failures explicitly, keep unsuccessful camera edits open, redact
  source credentials from list labels and avoid a loading flash during polling.
- Use native modal dialogs with keyboard containment, Escape close and focus
  restoration; improve focus visibility, input borders and close controls.
- Reject unauthenticated management API calls, cross-origin browser mutations,
  unsafe login return paths and the former empty-password GUI cookie.
- Update compatible locked dependencies and cookie validation. Three high-risk
  findings were removed; two low-risk SvelteKit advisories remain in npm audit,
  with documented application workarounds. See SECURITY-REVIEW.md.

This is source-level preparation, not a deployed standalone addon. Extaas Connect
adoption, relay authorization, bridge authorization and hardware/NVR acceptance
remain unfinished. No existing camera data was migrated or deleted.
