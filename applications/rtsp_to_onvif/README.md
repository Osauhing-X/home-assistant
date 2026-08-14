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
