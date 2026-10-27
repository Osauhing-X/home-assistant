# Standalone RTSP to ONVIF package — development acceptance

This build context is deliberately below `packaging/`, not a published top-level
Home Assistant addon. Do not present it as a completed paid service or move it
into the repository root before the release requirements are satisfied.

It builds the existing reviewed application from the exact public Git revision
in `APP_REVISION`. No moving application branch is fetched. Runtime: Node 24,
FFmpeg, iproute2 and checksum-verified MediaMTX 1.19.3. The default init process
must stay enabled because this image does not contain S6. Host networking and
NET_ADMIN/NET_RAW support the existing virtual camera addresses; no Supervisor
API or host configuration directory is requested by this package.

The bootstrap validates `/data/options.json`: a management password of at least
12 characters, GUI port and exact public HTTP(S) origin. No key is printed on
startup failure. It starts account linking but does not equate linking with paid
access. Existing X environment identifiers and the offline test flag are removed.

## Data migration boundary

The application path remains `/data/application-data/rtsp-to-onvif`, **inside the
new addon's own data volume**. It cannot automatically read the same path in X
Platform's separate volume. Do not delete the X application, mount both copies
read-write, or run both against one camera data directory.

Before real migration: back up X and its private RTSP directory, stop the old
camera application, transfer `cameras.json` and `settings.json` using an explicit
offline migration with validation, then verify permissions, ports, identities,
source credentials and recorder reconnection. If account linking already exists,
retain both `connect.json` and `.connect-key` together. Never post these files to
issues, source control or chat. Rollback must preserve the original stopped data.
An automated import/rollback tool and a real migration acceptance are still needed.

## Before promotion to a real addon

- Build and test amd64 and aarch64 images; verify Home Assistant Supervisor install,
  startup, shutdown, private storage and network discovery on actual hardware.
- Authenticate/retire the legacy X update endpoint and complete remaining protocol
  security work listed in the application's SECURITY-REVIEW.md.
- Connect verified production paid periods to server-side service access, preserving
  existing rights. A test ledger must not authorize this production addon.
- Complete the full camera UI/CVI and accessibility review, not only account views.
- Complete and test an explicit migration/rollback path before retiring the old app.
