# Workspace Core for Home Assistant

This add-on runs the same Workspace Core release as the standalone Docker installation. There is no separate X Platform manager or second package format.

Install the add-on and choose **Open Web UI**. Complete Workspace's own administrator setup. Packages, Applications, integrations, automation definitions, jobs and cron use Core's existing interfaces and persistent data.

Supported image architectures: amd64 and aarch64. Ingress and 32-bit ARM are not offered in this release. Native Home Assistant components remain HA-only integrations.

See DOCS.md for installation, networking and migration from X Platform. A real Supervisor installation still requires acceptance on the target HA host; container checks alone do not certify hardware or ingress.
