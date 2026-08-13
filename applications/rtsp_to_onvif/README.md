# RTSP to ONVIF

X Application that exposes existing RTSP streams as virtual ONVIF cameras. It
performs RTSP passthrough and does not transcode video.

## Setup

1. Set the required `PASSWORD` in the X Environment variables tab.
2. Open the application and add a camera with HQ and optional LQ RTSP URLs.
3. Let your ONVIF-compatible recorder or automation platform discover it.
4. Connect with the configured ONVIF credentials.

Typical uses include connecting an RTSP-only camera to an NVR, Home Assistant,
video-management software, or another system that discovers cameras via ONVIF.

The application listens for WS-Discovery on UDP 3702 and serves ONVIF Device
and Media endpoints on its configured X Application port. The UNVR must be able
to reach both the application and the original RTSP camera URLs.

Camera configuration is stored persistently under
`/data/application-data/rtsp-to-onvif` and survives application updates.

This first version provides Device/Media discovery and H.264 profile metadata.
It does not yet proxy media, transcode codecs, emit motion events, or implement
PTZ controls.
