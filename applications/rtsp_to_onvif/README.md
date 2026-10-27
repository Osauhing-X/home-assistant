# RTSP to ONVIF

X Application that exposes existing RTSP streams as virtual ONVIF cameras. It
relays RTSP through the X host with MediaMTX and does not transcode video.

## Setup

1. Set the required `PASSWORD` in the X Environment variables tab.
2. Open the application and add a camera with HQ and optional LQ RTSP URLs.
3. Let your ONVIF-compatible recorder or automation platform discover it.
4. Connect with the configured ONVIF credentials.

Typical uses include connecting an RTSP-only camera to an NVR, Home Assistant,
video-management software, or another system that discovers cameras via ONVIF.

The application listens for WS-Discovery on UDP 3702 and serves ONVIF Device
and Media endpoints on its configured ONVIF port. The recorder receives the
stream from the X host on RTSP port 8554.

Camera configuration is stored persistently under
`/data/application-data/rtsp-to-onvif` and survives application updates.

See `DOCS.md` for architecture, ports, UniFi Protect and troubleshooting details.
See [ONVIF authentication behavior](ONVIF-AUTH.md) for nonce/timestamp requirements,
PasswordText compatibility and the exact limits of replay protection.

## Snapshot and storage changes in 0.8.4

JPEG snapshots now require the camera's nonempty ONVIF credentials through HTTP
Digest, or an authenticated GUI session. GUI sessions expire after seven days;
password changes invalidate existing sessions. Upgrading from static cookie
hashes requires signing in again. The snapshot URI itself stays stable. Anonymous
requests return 401 rather than an image. Verify your recorder supplies its
configured ONVIF credentials when fetching snapshots.

Corrupt or unreadable configuration is reported and retained; it is not replaced
with an empty camera list. Back up the existing private data directory before an
update. The default path above is unchanged. Camera and relay files contain
source credentials and must remain private.

Extaas Connect account linking now has an opt-in implementation and a dedicated
account view; see [connection flow and verified limits](CONNECT.md). It does not
yet enforce production paid access. The standalone addon remains unfinished. See
[security review and remaining rollout requirements](SECURITY-REVIEW.md) for the
exact test scope and outstanding relay/bridge authorization work.

The [standalone development build](../../packaging/rtsp_to_onvif/README.md) passes
amd64 and emulated ARM64 container checks for normal startup, authentication and
clean shutdown. It includes a private offline migration tool, but is not yet a
published Home Assistant addon. Actual installation, camera/recorder behavior,
paid access and rollback still require acceptance.
