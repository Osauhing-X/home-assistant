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
The repository includes an offline copy tool with synthetic acceptance. Run it
from a checked-out repository on a machine with access to both private directories:

```sh
node packaging/rtsp_to_onvif/migrate-data.mjs \
  --source /absolute/stopped-x-private-rtsp-directory \
  --target /absolute/new-addon-private-rtsp-directory \
  --gui-port 8090 --acknowledge-source-stopped
```

The target's parent must exist, while the target itself must not exist. The tool
retains source bytes, excludes derived MediaMTX files, validates camera/connection
data and rejects colliding TCP ports. A failed copy retains an incomplete marker;
the addon bootstrap refuses to start that target. Inspect and recover from the
verified source/backup instead of removing the marker to bypass the failure.
The tool cannot prove that an external X process is stopped: that is an explicit
operator prerequisite. It never deletes the source or performs a live cutover.
Real Home Assistant migration and recorder rollback acceptance remain required.

## Before promotion to a real addon

- Build and test amd64 and aarch64 images; verify Home Assistant Supervisor install,
  startup, shutdown, private storage and network discovery on actual hardware.
- Authenticate/retire the legacy X update endpoint and complete remaining protocol
  security work listed in the application's SECURITY-REVIEW.md.
- Connect verified production paid periods to server-side service access, preserving
  existing rights. A test ledger must not authorize this production addon.
- Complete the full camera UI/CVI and accessibility review, not only account views.
- Verify the offline migration on actual addon volumes and test recorder rollback
  before retiring the old app.

The image acceptance workflow builds amd64 and arm64 (ARM through emulation),
refuses missing options and starts the normal production bootstrap with a
synthetic options file under Docker `--network none`. It checks login, private
camera API access, the account page and installed media/network executables.
It also sends the ordinary Docker stop signal and requires exit code 0 rather
than a forced-kill exit. The application closes relay/discovery/proxy resources;
the standalone runtime gives active GUI requests five seconds to finish.
An ephemeral camera record tests fresh, replayed and stale UsernameToken requests
on all four Device/Media endpoints plus the SOAP size limit. It has discovery off
and no camera/stream is contacted; no physical network alias is created.
This is container acceptance without a camera, not Home Assistant or physical
ARM hardware acceptance. No image is published by this workflow.
