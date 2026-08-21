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
- The X add-on has the `NET_ADMIN` and `NET_RAW` capabilities required to create
  a separate macvlan interface for every virtual camera.

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

## Multiple cameras and IP assignment

UniFi Protect cannot reliably adopt multiple ONVIF cameras from one IP address.
X therefore creates a separate virtual network interface, IP address and stable
generated MAC address for every camera.

- **DHCP** is the default. X stores the first assigned address and requests the
  same address again after a restart. If it is no longer available, the DHCP
  server may assign another one and X stores the replacement. **New** clears
  the saved lease and requests a different DHCP address. A router-side DHCP
  reservation remains the strongest guarantee that an adopted address never changes.
- **Static** lets the user enter the camera address. Use an unused address that
  is reserved outside the DHCP pool to prevent conflicts.

X does not automatically replace a manually selected static address. Changing
between DHCP and Static recreates only that camera's virtual interface.

Resolution and FPS are detected from the source with `ffprobe`. Configuration
is stored in `/data/application-data/rtsp-to-onvif` and survives code updates.

## UniFi Protect

The main compatibility testing has been performed with RTSP cameras from
multiple manufacturers and with ONVIF adoption and playback in UniFi UNVR.
Dahua and Hikvision NVR compatibility has not been tested, so their behaviour
is currently unknown.

Each camera has an **Advertise in discovery** policy: On Connect, Always, 10 minutes,
30 minutes, 1 hour, 2 hours, 3 hours, 12 hours, or Off. Timed policies start
when the camera is saved and automatically switch to Off when their period ends.
Turning discovery off, reaching the deadline, or deleting a camera sends a
WS-Discovery `Bye` message so compatible recorders can remove their cached
adoption candidate. **On Connect** is the default and turns discovery off after
the first authenticated recorder stream request. Other policies are not changed
by a recorder connection.

UniFi Protect maps ONVIF identity fields unusually: during adoption it uses the
device-information Model as its Name, while its Model is taken from the ONVIF
name scope. X cross-maps these two fields so the configured Name and Model are
shown correctly after adoption. Before adoption, Protect may still repeat the
scope value in both columns; this is a Protect discovery-list limitation.

Enable third-party camera discovery in Protect. If the ONVIF profile, Name,
Model, ports or stream address changes, remove the old camera and adopt it
again because Protect caches ONVIF metadata.

UniFi Protect may occasionally retain a second adoption candidate with the same
IP address after a camera has already been added. This is consistent with a
cached WS-Discovery candidate rather than a second virtual camera. Turn that
camera's **Advertise in discovery** policy to **Off** after adoption (or use the
default **On Connect** policy), wait for the `Bye` announcement to be processed,
and avoid adopting the duplicate entry. If Protect still shows it, restart its
camera-discovery view or remove the stale candidate in Protect.

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
