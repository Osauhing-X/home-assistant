# RTSP to ONVIF

RTSP to ONVIF presents an existing RTSP stream as a virtual ONVIF camera for
NVRs and software that support ONVIF but cannot add a plain RTSP URL directly.

## How it works

- WS-Discovery advertises cameras on UDP port `3702`.
- ONVIF Device and Media services use the configured HTTP port (`8091` by default).
- MediaMTX relays streams through X on RTSP port `8554`.

The relay is essential for systems such as UniFi Protect, which expect the
ONVIF service and RTSP stream to use the same host. X returns:

```text
rtsp://<X host>:8554/<camera-id>
```

MediaMTX pulls the source RTSP stream on demand. H.264 packets are passed
through without transcoding, preserving quality and minimizing delay.

## Requirements

- X uses host networking.
- UDP `3702`, the ONVIF port and TCP `8554` are reachable from the NVR.
- X can reach the original RTSP source.
- The source provides H.264 for broad NVR compatibility.
- The X image contains `ffmpeg`, `ffprobe` and `mediamtx`.

MediaMTX is installed by the X Dockerfile. Rebuild or reinstall the complete X
add-on after adding or changing this dependency. Reloading application code
alone cannot update the container image.

## Setup

1. Set the required GUI `PASSWORD` in Environment variables.
2. Open RTSP to ONVIF and select **Add camera**.
3. Enter the camera Name and Model.
4. Set the ONVIF username and password used for adoption.
5. Add the HQ RTSP URL and optionally an LQ RTSP URL.
6. Save and adopt the discovered camera with its ONVIF credentials.

Resolution and FPS are detected from the source with `ffprobe`. Configuration
is stored in `/data/application-data/rtsp-to-onvif` and survives code updates.

## UniFi Protect

Enable third-party camera discovery in Protect. If the ONVIF profile, Name,
Model, ports or stream address changes, remove the old camera and adopt it
again because Protect caches ONVIF metadata.

## Troubleshooting

### Snapshot works but live view keeps loading

Confirm that the terminal contains a successful source diagnostic:

```text
[RTSP] profile=prof0 camera=Camera target=10.0.0.191:554/stream reachable=yes codec=h264 resolution=1920x1080 fps=30/1
```

Also verify that MediaMTX is running, the NVR can reach X on TCP `8554`, and
`GetStreamUri` returns the X relay address instead of the source camera IP.

### Camera is not discovered

- Confirm Auto-discovery is enabled.
- Check UDP `3702` and multicast connectivity.
- Across VLANs, use manual/advanced adoption with the X host and ONVIF port.

### `spawn mediamtx ENOENT`

Rebuild or reinstall the X add-on. Application reload cannot install MediaMTX
into an already-built container.

## Current scope

The application supports discovery, authentication, device information, media
profiles, snapshots and HQ/LQ RTSP relay. PTZ, ONVIF motion events and video
transcoding are not currently implemented.
