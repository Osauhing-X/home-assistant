import { readFile, stat } from 'node:fs/promises';
import { ACTIVE_COMMAND_FILE, atomicWrite, audit, COMMAND_FILE, getConfig, saveConfig } from '../src/lib/server/store.js';
import { appDirectory, clearLog, setStatus, status } from './runtime.js';
import { applyStagedApplication, deleteApplication, installApplication, stageApplication, startApplication, stopApplication } from './applications.js';
import { deleteIntegration, installIntegration, installOfficialRepositoryIntegrations, skipIntegrationUpdate, syncIntegrations } from './integrations.js';
import { scanRepository } from './repositories.js';

let busy = false;

function withDiscovered(config, app) {
  const discovered = config.repositories.find((repo) => repo.fullName === app.repository)?.applications?.find((item) => item.id === app.id);
  if (!discovered) return app;
  return {
    ...app, ...discovered,
    pluginPath: app.pluginPath || discovered.path,
    port: app.port, install: app.install, build: app.build, start: app.start,
    env: app.env, updatePolicy: app.updatePolicy, enabled: app.enabled, gui: app.gui,
    envSchema: discovered.envSchema?.length ? discovered.envSchema : app.envSchema
  };
}

async function execute(command) {
  const config = await getConfig();
  if (command.type === 'sync-integrations') return syncIntegrations();
  if (command.type === 'scan-repository') {
    await scanRepository(command.repository, { pull: command.pull === true });
    await installOfficialRepositoryIntegrations(command.repository);
    const refreshed = await getConfig();
    for (const configuredApp of refreshed.apps.filter((item) => item.repository === command.repository)) {
      const app = withDiscovered(refreshed, configuredApp);
      // A manual repository rescan always refreshes version_copy, even when
      // the declared version has not changed.
      await stageApplication(app);
      if (app.updatePolicy === 'automatic') {
        await stopApplication(app);
        await applyStagedApplication(app);
      }
    }
    return;
  }
  if (command.type === 'update-integration') return installIntegration(command.integrationId);
  if (command.type === 'delete-integration') return deleteIntegration(command.integrationId);
  if (command.type === 'skip-integration-update') return skipIntegrationUpdate(command.integrationId);
  const configuredApp = config.apps.find((item) => item.id === command.appId);
  const app = configuredApp ? withDiscovered(config, configuredApp) : null;
  if (!app) return;
  if (command.type === 'delete-application') return deleteApplication(app);
  if (command.type === 'stop') return stopApplication(app);
  if (command.type === 'start') {
    if (command.manual) await clearLog(app.id);
    return startApplication(app);
  }
  if (command.type === 'restart') {
    await stopApplication(app);
    await new Promise((resolve) => setTimeout(resolve, 1200));
    if (command.manual) await clearLog(app.id);
    return startApplication(app);
  }
  if (command.type === 'install') return installApplication(app, false);
  if (command.type === 'reload-code' || command.type === 'update') {
    await stopApplication(app);
    return applyStagedApplication(app);
  }
}

export async function consumeCommands() {
  if (busy) return;
  busy = true;
  try {
    let commands = [];
    try { commands = JSON.parse(await readFile(COMMAND_FILE, 'utf8')); } catch {}
    if (!commands.length) return;
    const command = commands.shift();
    await atomicWrite(COMMAND_FILE, commands);
    await atomicWrite(ACTIVE_COMMAND_FILE, { ...command, startedAt: new Date().toISOString() });
    try {
      await execute(command);
    } catch (error) {
      const target = command.appId || command.integrationId || command.repository || 'manager';
      await audit('queue', target, 'failed', error.message);
      if (command.appId) await setStatus(command.appId, { state: 'error', error: error.message });
    }
  } finally {
    await atomicWrite(ACTIVE_COMMAND_FILE, null);
    busy = false;
  }
}

export async function scheduledUpdateCheck() {
  const config = await getConfig();
  const interval = Math.max(1800, Number(config.updateChecks?.interval || 86400));
  const last = config.updateChecks?.lastCheck ? new Date(config.updateChecks.lastCheck).getTime() : 0;
  if (Date.now() - last < interval * 1000) return;
  // Scheduled checks fetch repository metadata, but only stage application
  // code when its declared version differs from the installed version.
  for (const repository of config.repositories) await scanRepository(repository.fullName, { pull: true });
  const refreshed = await getConfig();
  for (const configuredApp of refreshed.apps) {
    const app = withDiscovered(refreshed, configuredApp);
    const discovered = refreshed.repositories.find((repo) => repo.fullName === app.repository)?.applications?.find((item) => item.id === app.id);
    if (!discovered?.version) continue;
    if (status[app.id]?.installedVersion === discovered.version) {
      await setStatus(app.id, { availableVersion: discovered.version, updateAvailable: false });
      continue;
    }
    await stageApplication(app);
    if (app.updatePolicy === 'automatic') {
      await stopApplication(app);
      await applyStagedApplication(app);
    }
  }
  refreshed.updateChecks = { ...refreshed.updateChecks, lastCheck: new Date().toISOString() };
  await saveConfig(refreshed);
  await audit('portal', 'updates', 'checked', `${refreshed.repositories.length} repositories`);
}

export async function boot() {
  await syncIntegrations();
  const config = await getConfig();
  for (const app of config.apps.filter((item) => item.enabled)) {
    try {
      await stat(appDirectory(app));
      if (status[app.id]?.installed) await startApplication(app);
      else await installApplication(app);
    } catch { await installApplication(app); }
  }
}
