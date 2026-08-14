import { cp, mkdir, rm, stat } from 'node:fs/promises';
import path from 'node:path';
import { audit, getConfig, saveConfig, tokenFor } from '../src/lib/server/store.js';
import { HA_COMPONENTS_DIR, INTEGRATIONS_DIR, log, repoDirectory, setStatus } from './runtime.js';
import { scanRepository } from './repositories.js';
import { notify } from './notifications.js';

export async function installIntegration(integrationId) {
  const config = await getConfig();
  const integration = config.integrations.find((item) => item.id === integrationId);
  if (!integration) return;
  const live = path.join(HA_COMPONENTS_DIR, integration.domain);
  const staged = path.join(live, 'new_version');
  const version = integration.stagedVersion || integration.version || 'unknown';
  let source = path.join(repoDirectory(integration.repository), integration.path);
  try { await stat(staged); source = staged; } catch {}
  const archive = path.join(INTEGRATIONS_DIR, integration.id, version);
  await rm(archive, { recursive: true, force: true });
  await cp(source, archive, { recursive: true, force: true });
  await rm(live, { recursive: true, force: true });
  await cp(archive, live, { recursive: true, force: true });
  Object.assign(integration, { installed: true, installedVersion: version, installedAt: new Date().toISOString(), stagedVersion: '', ignoredVersion: '', manualRemoval: false });
  await saveConfig(config);
  await log('x-installer', `Installed ${integration.name} ${version}`);
  await audit('integration', integration.id, 'installed', version);
  await notify('successfulUpdates', `Integration updated: ${integration.name}`, `Installed version ${version}.`);
}

export async function restartHomeAssistant() {
  const token = process.env.SUPERVISOR_TOKEN;
  if (!token) throw new Error('SUPERVISOR_TOKEN is unavailable; Home Assistant was not restarted');
  const response = await fetch('http://supervisor/core/restart', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
  });
  if (!response.ok) throw new Error(`Supervisor rejected Home Assistant restart with HTTP ${response.status}`);
}

export async function deleteIntegration(integrationId) {
  const config = await getConfig();
  const integration = config.integrations.find((item) => item.id === integrationId);
  if (!integration) return;
  await rm(path.join(HA_COMPONENTS_DIR, integration.domain), { recursive: true, force: true });
  await rm(path.join(INTEGRATIONS_DIR, integration.id), { recursive: true, force: true });
  Object.assign(integration, { installed: false, installedVersion: '', installedAt: null, manualRemoval: true });
  await saveConfig(config);
  await audit('integration', integration.id, 'deleted', integration.domain);
  await log('x-installer', `Deleted ${integration.name} from Home Assistant`);
}

export async function skipIntegrationUpdate(integrationId) {
  const config = await getConfig();
  const integration = config.integrations.find((item) => item.id === integrationId);
  if (!integration?.stagedVersion) return;
  await rm(path.join(HA_COMPONENTS_DIR, integration.domain, 'new_version'), { recursive: true, force: true });
  integration.ignoredVersion = integration.stagedVersion;
  integration.stagedVersion = '';
  await saveConfig(config);
  await audit('integration', integration.id, 'update_skipped', integration.ignoredVersion);
}

export async function syncIntegrations() {
  let config = await getConfig();
  if (!config.installer?.enabled) return;
  await mkdir(HA_COMPONENTS_DIR, { recursive: true });
  for (const fullName of config.repositories.filter((repository) => repository.official).map((repository) => repository.fullName)) {
    try {
      await scanRepository(fullName);
      config = await getConfig();
      for (const integration of config.integrations.filter((item) => item.repository === fullName && !item.installed && !item.manualRemoval)) await installIntegration(integration.id);
    } catch (error) {
      await log('x-installer', `Failed to sync ${fullName}: ${error.message}`, tokenFor(config));
      await notify('integrationErrors', `Integration sync failed: ${fullName}`, error.message);
    }
  }
  await setStatus('x-installer', { state: 'running', lastSync: new Date().toISOString(), error: '' });
}

export async function installOfficialRepositoryIntegrations(fullName) {
  const config = await getConfig();
  const repository = config.repositories.find((item) => item.fullName === fullName);
  if (!repository?.official) return;
  for (const integration of config.integrations.filter((item) => item.repository === fullName && !item.installed && !item.manualRemoval)) await installIntegration(integration.id);
}
