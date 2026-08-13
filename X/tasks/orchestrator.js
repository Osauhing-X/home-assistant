import { readFile, stat } from 'node:fs/promises';
import { atomicWrite, audit, COMMAND_FILE, getConfig, saveConfig } from '../src/lib/server/store.js';
import { appDirectory, setStatus, status } from './runtime.js';
import { applyStagedApplication, installApplication, stageApplication, startApplication, stopApplication } from './applications.js';
import { deleteIntegration, installIntegration, installOfficialRepositoryIntegrations, syncIntegrations } from './integrations.js';
import { scanRepository } from './repositories.js';

let busy = false;

async function execute(command) {
  const config = await getConfig();
  if (command.type === 'sync-integrations') return syncIntegrations();
  if (command.type === 'scan-repository') {
    await scanRepository(command.repository, { pull: command.pull === true });
    await installOfficialRepositoryIntegrations(command.repository);
    const refreshed = await getConfig();
    for (const app of refreshed.apps.filter((item) => item.repository === command.repository)) {
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
  if (command.type === 'update-all-integrations') {
    for (const integration of config.integrations.filter((item) => item.installed)) await installIntegration(integration.id);
    return;
  }
  const app = config.apps.find((item) => item.id === command.appId);
  if (!app) return;
  if (command.type === 'stop') return stopApplication(app);
  if (command.type === 'start') return startApplication(app);
  if (command.type === 'restart') {
    await stopApplication(app);
    setTimeout(() => startApplication(app), 1200).unref();
    return;
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
    await atomicWrite(COMMAND_FILE, []);
    for (const command of commands) await execute(command);
  } finally { busy = false; }
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
  for (const app of refreshed.apps) {
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
      await startApplication(app);
    } catch { await installApplication(app); }
  }
}
