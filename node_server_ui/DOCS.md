# Node.js Server Add-on Documentation

This document describes the configuration and internal behavior of the add-on.

---

## Setup

### 1️⃣ GitHub Token

Create a token here:
[https://github.com/settings/tokens](https://github.com/settings/tokens)

Use: **Personal access tokens (classic)**
Required permission: **repo** (for private repositories)

This allows access to private repositories.

Recommended: set expiration to **No expiration** to prevent unexpected service interruptions.

---

### 2️⃣ HA Add-on Configuration

**Repository format:**
```
USERNAME/REPOSITORY.git
```

Example:
```
myUser/discord-bot.git
```

---

**Environment variables format:**
```
NAME=VALUE
```

Example:
```
RANDOM=token_here PORT=3000 API_KEY=secret
```

Usage in Node.js:
```js
process.env.RANDOM
```

---

## Startup Process

When the add-on starts:

1. GitHub repositories are cloned
2. Dependencies are installed via `npm install`
3. `index.js` is executed
4. The process is monitored by the supervisor
5. If the process crashes, it is automatically restarted

---

## Repository Requirements

Each repository must contain:

* `index.js` (entry point)
* `package.json`

---

## Keep Alive

If your application does not contain any long-running processes (such as servers, intervals, or event listeners), it may exit immediately. In that case, you can keep the Node.js process alive using:

```js
setInterval(() => {}, 1000);
```

This keeps the event loop active and prevents the process from exiting.

Alternatively, the add-on provides a **Keep Alive** option per node, which automatically restarts the process if it exits. However, `setInterval` is preferred when you want a lightweight, explicit solution without relying on external supervision.

---

## Process Shutdown in Node.js

The add-on manages processes using system signals. Your application must handle these signals correctly to ensure clean shutdown and avoid orphan processes.

---

### SIGTERM (Graceful shutdown – required)

`SIGTERM` is sent by the add-on when stopping a process.
Your application should catch it and perform cleanup before exiting.

```js
process.on('SIGTERM', async () => {
  console.log('SIGTERM received - shutting down gracefully');

  await shutdown(); // close servers, DB connections, timers, etc.

  process.exit(0);
});
```

---

### SIGKILL (Force termination – no handling)

`SIGKILL` cannot be intercepted or handled by the application.
It is used only when the process does not stop after `SIGTERM`.

---

### Summary

* **SIGTERM** → graceful shutdown (you must implement this)
* **SIGKILL** → immediate termination (no cleanup possible)

Proper SIGTERM handling ensures clean shutdowns during stop or restart operations.

---

## Hardware Considerations

Each Node.js project has different resource requirements. Always evaluate whether your Home Automation (HA) hardware can handle the workload before deployment.

Ensure the system has sufficient CPU, memory, and overall performance capacity so that the Node.js application does not negatively impact other HA services.

Running heavy Node.js workloads on underpowered hardware—such as low-end Raspberry Pi devices or aging 10+ year-old systems—may lead to instability, high latency, or system-wide performance degradation.

---

## Troubleshooting

**Server does not start:**

* Verify `index.js` exists
* Verify `package.json` exists
* Verify dependencies were installed correctly

**Repository download fails:**

* Check GitHub token validity and permissions
* Verify repository format (`USERNAME/REPOSITORY.git`)
