# Installation and migration

1. Add https://github.com/Osauhing-X/home-assistant in the Home Assistant add-on store.
2. Install **Workspace Core** on an amd64 or aarch64 Home Assistant OS / Supervised host.
3. Select an available local web port (default 3010), start the add-on and choose **Open Web UI**.
4. Complete Core's administrator account setup. The HA session does not silently become a Core administrator session.

The add-on is the installer/runtime for Core, not an installer of a second container through the Docker socket. It has no Docker socket, host network, Supervisor API or Home Assistant API grant and does not mount the HA configuration directory. Supervisor control credentials are removed before Core starts. Persistent Core data, credentials, installed packages and installation identity are in /data and included in Supervisor backups.

## Networking

Use Core-internal access for Applications. Arbitrary dedicated Application ports are not automatically exposed through the add-on port map. Individually published domains/Cloudflare routes need explicit configuration. Public exposure is not enabled by installing this add-on. Ingress is intentionally disabled until root-relative links, assets and authentication have been tested through Supervisor ingress.

## Replacing X Platform

X Platform's manager has been retired from the repository. Its Git history remains available, but it is not a second maintained runtime. Existing installed X add-ons are not remotely uninstalled by this source change.

Before removing an installed X add-on, make a full Supervisor backup including its /data. Stop it, install Workspace Core separately, then migrate supported package data deliberately. The old manager's registry is not a Core registry: copying its JSON file over Core data is unsupported. Do not delete the old add-on/data until its Applications and records have been checked in the replacement.

RTSP to ONVIF remains a separate add-on package under packaging/rtsp_to_onvif; it is not automatically started or bundled here. Other former X Applications require a Workspace manifest/data adapter before they can run in Core; the installer does not claim automatic conversion.

## Native HA entities

The package integrations/x_entities has a Workspace manifest restricting it to home-assistant. Its actual Python integration is custom_components/extaas_com, with its own native HA manifest. Install that folder using HA's custom component process and restart HA. It is not automatically written into HA configuration by this add-on. Core-mode connectivity is read-only and uses /health; legacy entity publishers must authenticate to the HA API.
