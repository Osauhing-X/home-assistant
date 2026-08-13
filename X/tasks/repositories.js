import { cp, readFile, readdir, rm, stat } from 'node:fs/promises';
import path from 'node:path';
import { audit, getConfig, saveConfig, tokenFor } from '../src/lib/server/store.js';
import { HA_COMPONENTS_DIR, repoDirectory, shell } from './runtime.js';
import { notify } from './notifications.js';

function gitEnvironment(token) {
  const env = { ...process.env, GITHUB_TOKEN: token || '', GIT_TERMINAL_PROMPT: '0' };
  if (token) {
    env.GIT_CONFIG_COUNT = '1';
    env.GIT_CONFIG_KEY_0 = 'http.https://github.com/.extraheader';
    env.GIT_CONFIG_VALUE_0 = `AUTHORIZATION: basic ${Buffer.from(`x-access-token:${token}`).toString('base64')}`;
  }
  return env;
}

export async function checkout(repository, branch = '', update = false) {
  const config = await getConfig();
  const repositoryConfig = config.repositories.find((item) => item.fullName === repository);
  const directory = repoDirectory(repository);
  const token = tokenFor(config, repositoryConfig?.accountId);
  try {
    await stat(path.join(directory, '.git'));
    if (update) await shell('git pull --ff-only', { cwd: directory, env: gitEnvironment(token) });
  } catch {
    await rm(directory, { recursive: true, force: true });
    const branchArgument = branch ? `--branch ${JSON.stringify(branch)}` : '';
    await shell(`git clone --depth 1 ${branchArgument} ${JSON.stringify(`https://github.com/${repository}.git`)} ${JSON.stringify(directory)}`, { env: gitEnvironment(token) });
  }
  return directory;
}

async function walk(directory, depth = 4, current = '') {
  if (depth < 0) return [];
  const result = [];
  for (const entry of await readdir(path.join(directory, current), { withFileTypes: true })) {
    if (entry.name === '.git' || entry.name === 'node_modules' || entry.name === 'build') continue;
    const relative = path.join(current, entry.name);
    if (entry.isDirectory()) result.push(...await walk(directory, depth - 1, relative));
    else result.push(relative);
  }
  return result;
}

export async function scanRepository(fullName, { pull = false } = {}) {
  const config = await getConfig();
  const repository = config.repositories.find((item) => item.fullName === fullName);
  if (!repository) return;
  repository.scanState = 'scanning';
  await saveConfig(config);
  try {
    const root = await checkout(fullName, repository.branch, pull);
    const files = await walk(root);
    const integrations = [];
    const applications = [];
    for (const relative of files.filter((file) => path.basename(file) === 'manifest.json')) {
      try {
        const manifest = JSON.parse(await readFile(path.join(root, relative), 'utf8'));
        if (manifest.domain && (manifest.x === true || relative.includes('custom_components') || relative.startsWith(`integrations${path.sep}`) || relative.startsWith(`plugins${path.sep}`))) {
          integrations.push({ id: `${repository.id}--${manifest.domain}`, domain: manifest.domain, name: manifest.name || manifest.domain, version: manifest.version || '', path: path.dirname(relative), repository: fullName });
        }
      } catch {}
    }
    for (const relative of files.filter((file) => ['x_config.json', 'x-plugin.json'].includes(path.basename(file)))) {
      try {
        const value = JSON.parse(await readFile(path.join(root, relative), 'utf8'));
        const entries = Array.isArray(value.applications) ? value.applications : value.type === 'application' || value.start ? [value] : [];
        for (const item of entries) applications.push({ ...item, id: item.id || path.basename(path.dirname(relative)), name: item.name || item.id, path: item.path || path.dirname(relative), repository: fullName });
      } catch {}
    }
    Object.assign(repository, { integrations, applications, scanState: 'ready', scannedAt: new Date().toISOString() });
    const detectedIntegrationIds = new Set(integrations.map((item) => item.id));
    config.integrations = config.integrations.filter((item) => item.repository !== fullName || item.installed || detectedIntegrationIds.has(item.id));
    for (const integration of integrations) {
      const existing = config.integrations.find((item) => item.id === integration.id);
      if (existing) Object.assign(existing, integration, { availableVersion: integration.version });
      else config.integrations.push({ ...integration, installedVersion: '', installed: false });
    }
    await saveConfig(config);
    for (const integration of config.integrations.filter((item) => item.repository === fullName && item.installed)) {
      const staged = path.join(HA_COMPONENTS_DIR, integration.domain, 'new_version');
      if (!integration.version || integration.installedVersion === integration.version) {
        await rm(staged, { recursive: true, force: true });
        integration.stagedVersion = '';
        integration.ignoredVersion = '';
        continue;
      }
      if (integration.ignoredVersion === integration.version) {
        integration.stagedVersion = '';
        continue;
      }
      await rm(staged, { recursive: true, force: true });
      await cp(path.join(root, integration.path), staged, { recursive: true, force: true });
      integration.stagedVersion = integration.version;
      if (integration.ignoredVersion && integration.ignoredVersion !== integration.version) integration.ignoredVersion = '';
      // Bootstrap the manager-owned X Entities updater itself. The remaining
      // integration stays staged until Home Assistant installs it.
      if (integration.domain === 'extaas_com') {
        for (const file of ['const.py', 'api.py', 'update.py']) {
          await cp(path.join(root, integration.path, file), path.join(HA_COMPONENTS_DIR, integration.domain, file), { force: true });
        }
      }
      await audit('integration', integration.id, 'update_available', `${integration.installedVersion} -> ${integration.version}`);
    }
    await saveConfig(config);
    await audit('repository', fullName, 'scanned', `${integrations.length} integrations, ${applications.length} applications`);
    const updates = config.integrations.filter((item) => item.repository === fullName && item.installed && item.stagedVersion && item.installedVersion !== item.stagedVersion);
    if (updates.length) await notify('updatesAvailable', `Updates available from ${fullName}`, updates.map((item) => `${item.name}: ${item.installedVersion} -> ${item.stagedVersion}`).join('\n'));
  } catch (error) {
    repository.scanState = 'error';
    repository.scanError = error.message;
    await saveConfig(config);
    await notify('repositoryErrors', `Repository scan failed: ${fullName}`, error.message);
  }
}
