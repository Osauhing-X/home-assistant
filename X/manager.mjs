import { spawn } from 'node:child_process';
import { appendFile, cp, mkdir, readFile, readdir, rm, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { atomicWrite, audit, COMMAND_FILE, DATA_DIR, getConfig, saveConfig, STATUS_FILE, tokenFor } from './src/lib/server/store.js';

const REPOSITORIES_DIR = path.join(DATA_DIR, 'repositories');
const LOGS_DIR = path.join(DATA_DIR, 'logs');
const INTEGRATIONS_DIR = path.join(DATA_DIR, 'integrations');
const HA_COMPONENTS_DIR = process.env.HA_COMPONENTS_DIR || '/homeassistant/custom_components';
const children = new Map();
let status = {};
let busy = false;

await mkdir(REPOSITORIES_DIR, { recursive: true });
await mkdir(LOGS_DIR, { recursive: true });
await mkdir(INTEGRATIONS_DIR, { recursive: true });
try { status = JSON.parse(await readFile(STATUS_FILE, 'utf8')); } catch { status = {}; }

function repoDirectory(repository) {
  return path.join(REPOSITORIES_DIR, repository.replace('/', '__'));
}

function appDirectory(app) {
  const root = path.resolve(repoDirectory(app.repository));
  const selected = path.resolve(root, app.pluginPath || '.');
  if (selected !== root && !selected.startsWith(`${root}${path.sep}`)) throw new Error('Plugin path leaves the repository.');
  return selected;
}

function redact(message, token) {
  return token ? String(message).split(token).join('[secret]') : String(message);
}

async function log(id, message, token = '') {
  const line = `[${new Date().toISOString()}] ${redact(message, token)}`;
  await appendFile(path.join(LOGS_DIR, `${id}.log`), `${line}\n`);
  console.log(`[${id}] ${redact(message, token)}`);
}

async function setStatus(id, patch) {
  status[id] = { state: 'stopped', ...status[id], ...patch, updatedAt: new Date().toISOString() };
  await atomicWrite(STATUS_FILE, status);
}

function shell(command, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn('/bin/sh', ['-lc', command], { ...options, stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '';
    child.stdout.on('data', (data) => { output += data; options.onData?.(data.toString()); });
    child.stderr.on('data', (data) => { output += data; options.onData?.(data.toString()); });
    child.once('error', reject);
    child.once('exit', (code) => code === 0 ? resolve(output) : reject(new Error(`Command exited with ${code}: ${output.slice(-2000)}`)));
  });
}

function gitEnvironment(token) {
  const env = { ...process.env, GITHUB_TOKEN: token || '', GIT_TERMINAL_PROMPT: '0' };
  if (token) {
    env.GIT_CONFIG_COUNT = '1';
    env.GIT_CONFIG_KEY_0 = 'http.https://github.com/.extraheader';
    env.GIT_CONFIG_VALUE_0 = `AUTHORIZATION: basic ${Buffer.from(`x-access-token:${token}`).toString('base64')}`;
  }
  return env;
}

async function checkout(repository, branch = '', update = false) {
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
    const remote = `https://github.com/${repository}.git`;
    await shell(`git clone --depth 1 ${branchArgument} ${JSON.stringify(remote)} ${JSON.stringify(directory)}`, { env: gitEnvironment(token) });
  }
  return directory;
}

async function detectIntegration(app) {
  if (app.homeAssistant?.discovery) return { recommended: true, reason: 'Declared by the plugin manifest' };
  const directory = appDirectory(app);
  const candidates = ['index.js', 'src/index.js', 'server.js'];
  for (const candidate of candidates) {
    try {
      const source = await readFile(path.join(directory, candidate), 'utf8');
      if (/extaas_com|nodeData|bonjour.*publish/s.test(source)) return { recommended: true, reason: `Entity discovery code found in ${candidate}` };
    } catch {}
  }
  return { recommended: false, reason: '' };
}

async function install(app, update = false) {
  await setStatus(app.id, { state: update ? 'updating' : 'installing', error: '' });
  const config = await getConfig();
  const token = tokenFor(config, config.repositories.find((item) => item.fullName === app.repository)?.accountId);
  try {
    await checkout(app.repository, app.branch, update);
    const cwd = appDirectory(app);
    const writeLog = (data) => log(app.id, data.trimEnd(), token);
    if (app.install) await shell(app.install, { cwd, env: process.env, onData: writeLog });
    if (app.build) await shell(app.build, { cwd, env: process.env, onData: writeLog });
    const recommendation = await detectIntegration(app);
    let installedVersion = app.version || 'unknown';
    try { installedVersion = JSON.parse(await readFile(path.join(cwd, 'package.json'), 'utf8')).version || installedVersion; } catch {}
    await setStatus(app.id, { state: 'stopped', installed: true, installedVersion, availableVersion: installedVersion, error: '', recommendation });
    if (app.enabled) await start(app);
  } catch (error) {
    await log(app.id, error.message, token);
    await notify('applicationErrors', `Application ${app.name} failed`, error.message);
    await setStatus(app.id, { state: 'error', error: redact(error.message, token) });
  }
}

async function start(app) {
  if (children.has(app.id)) return;
  const directory = appDirectory(app);
  const config = await getConfig();
  const repository = config.repositories.find((item) => item.fullName === app.repository);
  const env = {
    ...process.env,
    ...(repository?.env || {}),
    ...(app.env || {}),
    HOST: '0.0.0.0',
    PORT: String(app.port),
    X_PLATFORM: 'true'
  };
  const child = spawn('/bin/sh', ['-lc', app.start], { cwd: directory, env, stdio: ['ignore', 'pipe', 'pipe'], detached: false });
  children.set(app.id, child);
  await setStatus(app.id, { state: 'running', pid: child.pid, error: '', port: app.port });
  child.stdout.on('data', (data) => log(app.id, data.toString().trimEnd()));
  child.stderr.on('data', (data) => log(app.id, data.toString().trimEnd()));
  child.once('exit', async (code, signal) => {
    children.delete(app.id);
    await setStatus(app.id, { state: code === 0 || signal === 'SIGTERM' ? 'stopped' : 'error', pid: null, error: code ? `Exited with code ${code}` : '' });
    if (code) await notify('applicationStopped', `Application ${app.name} stopped`, `The process exited with code ${code}.`);
  });
  await audit('application', app.id, 'started', `port ${app.port}`);
}

async function notify(type, title, message) {
  try {
    const config = await getConfig();
    if (config.notifications?.[type] === false) return;
    await fetch('http://127.0.0.1:3099/api/notify', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title, message }) });
  }
  catch {}
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

async function scanRepository(fullName) {
  const config = await getConfig();
  const repository = config.repositories.find((item) => item.fullName === fullName);
  if (!repository) return;
  repository.scanState = 'scanning';
  await saveConfig(config);
  try {
    const root = await checkout(fullName, repository.branch, true);
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
    const configs = files.filter((file) => ['x_config.json', 'x-plugin.json'].includes(path.basename(file)));
    for (const relative of configs) {
      try {
        const value = JSON.parse(await readFile(path.join(root, relative), 'utf8'));
        const entries = Array.isArray(value.applications) ? value.applications : value.type === 'application' || value.start ? [value] : [];
        for (const item of entries) applications.push({ ...item, id: item.id || path.basename(path.dirname(relative)), name: item.name || item.id, path: item.path || path.dirname(relative), repository: fullName });
      } catch {}
    }
    repository.integrations = integrations;
    repository.applications = applications;
    repository.scanState = 'ready';
    repository.scannedAt = new Date().toISOString();
    for (const integration of integrations) {
      const existing = config.integrations.find((item) => item.id === integration.id);
      if (existing) Object.assign(existing, integration, { availableVersion: integration.version });
      else config.integrations.push({ ...integration, installedVersion: '', installed: false });
    }
    await saveConfig(config);
    for (const integration of config.integrations.filter((item) => item.repository === fullName && item.installed && item.version && item.installedVersion !== item.version)) {
      const source = path.join(root, integration.path);
      const staged = path.join(HA_COMPONENTS_DIR, integration.domain, 'new_version');
      await rm(staged, { recursive: true, force: true });
      await cp(source, staged, { recursive: true, force: true });
      await audit('integration', integration.id, 'update_available', `${integration.installedVersion} -> ${integration.version}`);
    }
    await audit('repository', fullName, 'scanned', `${integrations.length} integrations, ${applications.length} applications`);
    const updates = config.integrations.filter((item) => item.repository === fullName && item.installed && item.version && item.installedVersion !== item.version);
    if (updates.length) await notify('updatesAvailable', `Updates available from ${fullName}`, updates.map((item) => `${item.name}: ${item.installedVersion} → ${item.version}`).join('\n'));
  } catch (error) {
    repository.scanState = 'error'; repository.scanError = error.message;
    await saveConfig(config); await notify('repositoryErrors', `Repository scan failed: ${fullName}`, error.message);
  }
}

async function installIntegration(integrationId) {
  const config = await getConfig();
  const integration = config.integrations.find((item) => item.id === integrationId);
  if (!integration) return;
  const source = path.join(repoDirectory(integration.repository), integration.path);
  const archive = path.join(INTEGRATIONS_DIR, integration.id, integration.version || 'unknown');
  await rm(archive, { recursive: true, force: true });
  await cp(source, archive, { recursive: true, force: true });
  await rm(path.join(HA_COMPONENTS_DIR, integration.domain), { recursive: true, force: true });
  await cp(archive, path.join(HA_COMPONENTS_DIR, integration.domain), { recursive: true, force: true });
  integration.installed = true; integration.installedVersion = integration.version; integration.installedAt = new Date().toISOString();
  await saveConfig(config);
  await log('x-installer', `Installed ${integration.name} ${integration.version}`);
  await audit('integration', integration.id, 'installed', integration.version || 'unknown');
  await notify('successfulUpdates', `Integration updated: ${integration.name}`, `Installed version ${integration.version || 'unknown'}.`);
}

async function stop(app) {
  const child = children.get(app.id);
  if (!child) return setStatus(app.id, { state: 'stopped', pid: null });
  child.kill('SIGTERM');
  await audit('application', app.id, 'stopped');
  setTimeout(() => { if (children.has(app.id)) child.kill('SIGKILL'); }, 5000).unref();
}

async function syncIntegrations() {
  let config = await getConfig();
  if (!config.installer?.enabled) return;
  await mkdir(HA_COMPONENTS_DIR, { recursive: true });
  for (const fullName of config.installer.repositories || []) {
    try {
      if (!config.repositories.some((item) => item.fullName === fullName)) {
        config.repositories.push({ id: fullName.replace('/', '__').toLowerCase(), fullName, accountId: '', branch: '', env: {}, integrations: [], applications: [], scanState: 'queued' });
        await saveConfig(config);
      }
      await scanRepository(fullName);
      config = await getConfig();
      for (const integration of config.integrations.filter((item) => item.repository === fullName && item.domain === 'extaas_com')) {
        await installIntegration(integration.id);
      }
    } catch (error) {
      await log('x-installer', `Failed to sync ${fullName}: ${error.message}`, tokenFor(config));
      await notify('integrationErrors', `Integration sync failed: ${fullName}`, error.message);
    }
  }
  await setStatus('x-installer', { state: 'running', lastSync: new Date().toISOString(), error: '' });
}

async function execute(command) {
  const config = await getConfig();
  if (command.type === 'sync-integrations') return syncIntegrations();
  if (command.type === 'scan-repository') return scanRepository(command.repository);
  if (command.type === 'update-integration') return installIntegration(command.integrationId);
  if (command.type === 'update-all-integrations') {
    for (const integration of config.integrations) await installIntegration(integration.id);
    return;
  }
  const app = config.apps.find((item) => item.id === command.appId);
  if (!app) return;
  if (command.type === 'stop') return stop(app);
  if (command.type === 'start') return start(app);
  if (command.type === 'restart') { await stop(app); setTimeout(() => start(app), 1200).unref(); return; }
  if (command.type === 'install') return install(app, false);
  if (command.type === 'update') { await stop(app); return install(app, true); }
}

async function consumeCommands() {
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

async function scheduledUpdateCheck() {
  const config = await getConfig();
  const interval = Math.max(1800, Number(config.updateChecks?.interval || 86400));
  const last = config.updateChecks?.lastCheck ? new Date(config.updateChecks.lastCheck).getTime() : 0;
  if (Date.now() - last < interval * 1000) return;
  for (const repository of config.repositories) await scanRepository(repository.fullName);
  const refreshed = await getConfig();
  for (const app of refreshed.apps) {
    const discovered = refreshed.repositories.find((repo) => repo.fullName === app.repository)?.applications?.find((item) => item.id === app.id);
    if (!discovered?.version) continue;
    await setStatus(app.id, { availableVersion: discovered.version, updateAvailable: status[app.id]?.installedVersion !== discovered.version });
    if (app.updatePolicy === 'automatic' && status[app.id]?.installedVersion !== discovered.version) await install(app, true);
  }
  refreshed.updateChecks = { ...refreshed.updateChecks, lastCheck: new Date().toISOString() };
  await saveConfig(refreshed);
  await audit('portal', 'updates', 'checked', `${refreshed.repositories.length} repositories`);
}

async function boot() {
  const config = await getConfig();
  await syncIntegrations();
  for (const app of config.apps.filter((item) => item.enabled)) {
    try {
      await stat(appDirectory(app));
      await start(app);
    } catch { await install(app); }
  }
}

process.on('SIGTERM', () => { for (const child of children.values()) child.kill('SIGTERM'); process.exit(0); });
process.on('SIGINT', () => { for (const child of children.values()) child.kill('SIGTERM'); process.exit(0); });

await boot();
setInterval(consumeCommands, 1000);
setInterval(scheduledUpdateCheck, 60000);
setInterval(syncIntegrations, Math.max(60, (await getConfig()).installer.interval || 3600) * 1000);
console.log(`[X Platform] Manager ready (${fileURLToPath(import.meta.url)})`);
