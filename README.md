<p align="center">
  <img src="./X/logo.png" alt="X Platform logo" width="96">
</p>

<h1 align="center">X for Home Assistant</h1>

<p align="center">
  <strong>One place for applications, integrations and the services that make a smart home feel complete.</strong>
</p>

<p align="center">
  Built by <a href="https://oux.ee">OUX — Osaühing X</a> · Part of the <a href="https://extaas.com">Extaas</a> technology ecosystem
</p>

---

## A smarter way to extend Home Assistant

This repository brings together the **X Platform**, Home Assistant integrations and full web applications in one local-first environment. Instead of managing a growing collection of separate add-ons, X gives you a central console for discovering, installing and operating the tools that belong around your home.

Connect repositories, install what you need and keep an eye on applications, integrations, updates, queues and logs from one consistent interface.

## What is included

| Project | Type | What it brings |
| --- | --- | --- |
| [**X Platform**](./X/) | Home Assistant add-on | The central launcher and management console for repositories, applications, integrations, configuration, updates and logs. |
| [**Popcorn**](./applications/popcorn/) | X application | A home-friendly movie discovery experience with personal and shared lists, reminders and Home Assistant controls. |
| [**RTSP to ONVIF**](./applications/rtsp_to_onvif/) | X application | Turns existing RTSP streams into discoverable virtual ONVIF cameras without transcoding the video. |
| [**X Entities**](./integrations/x_entities/) | Home Assistant integration | Connects X Platform and compatible applications to Home Assistant devices, entities, controls and update information. |

## Why X

- **One clear workspace** — launch graphical applications or open the X console from a simple start screen.
- **Built for repositories** — discover multiple applications and integrations from official or custom GitHub sources.
- **Made to be managed** — install, configure, start, stop and inspect applications without jumping between separate add-ons.
- **Home Assistant aware** — surface application health, controls, notifications and compatible entities inside Home Assistant.
- **Local by design** — applications run on your Home Assistant host and can expose their own interfaces on your local network.
- **Open to new ideas** — trusted custom projects can follow the X metadata conventions and become part of the same experience.

## How it fits together

```text
GitHub repositories
        │
        ▼
   X Platform
   ├── Applications ── web interfaces, services, ENV and logs
   └── Integrations ── Home Assistant devices and entities
```

## Get started

1. Add this repository to Home Assistant using the button below.
2. Install and start the **X Platform** add-on.
3. Open X, enter the console and choose the applications and integrations you want to use.

[![Add this repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/Osauhing-X/home-assistant)

> [!IMPORTANT]
> Custom applications run with access to the X add-on environment and may use the Home Assistant API. Install only repositories and code you trust.

## Documentation

This page is the map, not the manual. Setup instructions, configuration options and troubleshooting details live alongside each project:

- [X Platform guide](./X/README.md)
- [Popcorn guide](./applications/popcorn/README.md)
- [RTSP to ONVIF guide](./applications/rtsp_to_onvif/README.md) and [technical notes](./applications/rtsp_to_onvif/DOCS.md)
- [X Entities guide](./integrations/x_entities/README.md)

## OUX and Extaas

[OUX](https://oux.ee) creates practical digital solutions, brings systems online and develops technology around real needs. [Extaas](https://extaas.com) is where those tools, product experiences and new ideas come together — including our work for smarter homes.

If this project makes your setup better, you can help support its continued development:

[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-2.svg
[![Buy me a coffee][buymeacoffee-shield]](https://www.buymeacoffee.com/extaas)
