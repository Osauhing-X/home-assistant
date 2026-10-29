# Workspace for Home Assistant

Install the same **Workspace Core** used by standalone Docker as a Home Assistant add-on. There is one maintained package manager and runtime; the separate X Platform has been retired from this repository.

[Add this repository to Home Assistant](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/Osauhing-X/home-assistant)

## Packages

| Content | Purpose | Status |
| --- | --- | --- |
| [Workspace Core](workspace/) | Home Assistant installer/runtime for the shared Core image. Modules, integrations, Applications, automations, cron and jobs use the same Core. | amd64/aarch64 add-on; real HA host acceptance required. |
| [Home Assistant Entities](integrations/x_entities/) | Native HA custom component, with a separate Workspace manifest restricted to home-assistant. | Read-only Core connectivity plus retained legacy publishers; native install/restart required. |
| [RTSP to ONVIF](packaging/rtsp_to_onvif/) | Separate camera bridge add-on package. | Staged package; not automatically bundled with Workspace. |
| [Legacy Applications](applications/) | Existing application sources, including Popcorn. | Not automatically converted to Workspace manifests or data contracts. |

## Replacing an existing X installation

Back up its complete Supervisor data before removing it. The new workspace_core add-on has its own persistent /data; the old X manager registry is not a Core registry and must not overwrite it. Keep the stopped old installation/backup until supported application data has been checked in Core. This source change does not uninstall or delete an already installed HA add-on.

See [Workspace installation and migration](workspace/DOCS.md). Previous X code remains recoverable in Git history; no second X runtime is maintained at HEAD. Native HA domain extaas_com is retained so existing entities do not need blanket deletion/recreation.

Package host compatibility and capabilities determine whether a package runs on a host. Compatibility does not grant device access, HA control, credentials or permission to execute untrusted code.
