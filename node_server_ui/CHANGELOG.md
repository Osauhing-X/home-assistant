# Changelog

All significant changes to the project are documented below.

---

## Version 04.2026

Major evolution of the original **"Node Server" add-on** into a full-featured add-on project with a user interface and extended functionality.

### Added

* Web UI for managing Node.js services
* Real-time log streaming per node
* Per-node keep-alive control

### Implemented

* SIGTERM and SIGKILL process handling

### Notes

* Project restructuring and migration from the original base implementation

---

## Version 2.0

### Added

* Multi-repository support
* Environment variable configuration support
* Automatic restart mechanism for failed services

### Improved

* Stability when running multiple concurrent services
* Enhanced error handling during repository cloning and setup

---

## Version 1.0

Initial release.

### Features

* Single repository support
* Automatic dependency installation via npm
* Node.js execution using `index.js` as entry point
