import { spawn } from 'node:child_process';
import { cp, mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { audit, DATA_DIR, getConfig, tokenFor } from '../src/lib/server/store.js';
import { appDirectory, appSourceDirectory, appVersionCopyDirectory, children, log, redact, setStatus, shell, status } from './runtime.js';
import { notify } from './notifications.js';

async function installEnvironment() {
  const env = { ...process.env };
  for (const key of Object.keys(env)) {
    if (['npm_config_global_style', 'npm_config_install_strategy', 'npm_config_omit', 'npm_config_production', 'npm_config_userconfig', 'npm_config_globalconfig', 'npm_config_include', 'node_env'].includes(key.toLowerCase())) delete env[key];
  }
  const npmConfigDirectory = path.join(DATA_DIR, 'runtime', 'npm');
  const userConfig = path.join(npmConfigDirectory, 'user.npmrc');
  const globalConfig = path.join(npmConfigDirectory, 'global.npmrc');
  await mkdir(npmConfigDirectory, { recursive: true });
  await Promise.all([writeFile(userConfig, ''), writeFile(globalConfig, '')]);
  Object.assign(env, {
    NODE_ENV: 'development',
    NPM_CONFIG_INSTALL_STRATEGY: 'hoisted',
    NPM_CONFIG_INCLUDE: 'dev',
    NPM_CONFIG_USERCONFIG: userConfig,
    NPM_CONFIG_GLOBALCONFIG: globalConfig
  });
  return env;
}

async function detectIntegration(app) {
  if (app.homeAssistant?.discovery) return { recommended: true, reason: 'Declared by the plugin manifest' };
  const directory = appDirectory(app);
  for (const candidate of ['index.js', 'src/index.js', 'server.js']) {
    try {
      const source = await readFile(path.join(directory, candidate), 'utf8');
      if (/extaas_com|nodeData|bonjour.*publish/s.test(source)) return { recommended: true, reason: `Entity discovery code found in ${candidate}` };
    } catch {}
  }
  return { recommended: false, reason: '' };
}

export async function installApplication(app, update = false) {
  await setStatus(app.id, { state: update ? 'updating' : 'installing', error: '' });
  const config = await getConfig();
  const token = tokenFor(config, config.repositories.find((item) => item.fullName === app.repository)?.accountId);
  try {
    const active = appDirectory(app);
    const source = appSourceDirectory(app);
    if (!update) {
      await rm(active, { recursive: true, force: true });
      await cp(source, active, { recursive: true });
    }
    const cwd = appDirectory(app);
    const writeLog = (data) => log(app.id, data.trimEnd(), token);
    const env = await installEnvironment();
    const installCommand = app.install?.trim() === 'npm ci'
      ? 'npm install --include=dev --install-strategy=hoisted'
      : app.install;
    if (installCommand) await shell(installCommand, { cwd, env, onData: writeLog });
    if (app.build) await shell(app.build, { cwd, env, onData: writeLog });
    let installedVersion = app.version || '';
    if (!installedVersion) {
      try { installedVersion = JSON.parse(await readFile(path.join(cwd, 'package.json'), 'utf8')).version || ''; } catch {}
    }
    installedVersion ||= 'unknown';
    await setStatus(app.id, { state: 'stopped', installed: true, installedVersion, availableVersion: installedVersion, updateAvailable: false, error: '', recommendation: await detectIntegration(app) });
    if (app.enabled) await startApplication(app);
  } catch (error) {
    await log(app.id, error.message, token);
    await notify('applicationErrors', `Application ${app.name} failed`, error.message);
    await setStatus(app.id, { state: 'error', error: redact(error.message, token) });
  }
}

export async function stageApplication(app) {
  const active = appDirectory(app);
  try { await stat(active); } catch { return; }
  const staged = appVersionCopyDirectory(app);
  await rm(path.join(active, 'github_copy'), { recursive: true, force: true });
  await rm(staged, { recursive: true, force: true });
  await cp(appSourceDirectory(app), staged, { recursive: true });
  let availableVersion = app.version || '';
  if (!availableVersion) {
    try { availableVersion = JSON.parse(await readFile(path.join(staged, 'package.json'), 'utf8')).version || ''; } catch {}
  }
  availableVersion ||= 'unknown';
  const updateAvailable = Boolean(status[app.id]?.installedVersion && status[app.id].installedVersion !== availableVersion);
  await setStatus(app.id, { availableVersion, updateAvailable, stagedAt: new Date().toISOString() });
}

export async function applyStagedApplication(app) {
  const active = appDirectory(app);
  const staged = appVersionCopyDirectory(app);
  await stat(staged);
  const temporary = `${active}.next`;
  await rm(temporary, { recursive: true, force: true });
  await cp(staged, temporary, { recursive: true });
  await rm(active, { recursive: true, force: true });
  await cp(temporary, active, { recursive: true });
  await cp(temporary, appVersionCopyDirectory(app), { recursive: true });
  await rm(temporary, { recursive: true, force: true });
  await installApplication(app, true);
}

export async function startApplication(app) {
  if (children.has(app.id)) return;
  const directory = appDirectory(app);
  const config = await getConfig();
  const repository = config.repositories.find((item) => item.fullName === app.repository);
  const env = { ...process.env, ...(repository?.env || {}), ...(app.env || {}), HOST: '0.0.0.0', PORT: String(app.port), X_PLATFORM: 'true' };
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

export async function stopApplication(app) {
  const child = children.get(app.id);
  if (!child) return setStatus(app.id, { state: 'stopped', pid: null });
  child.kill('SIGTERM');
  await audit('application', app.id, 'stopped');
  setTimeout(() => { if (children.has(app.id)) child.kill('SIGKILL'); }, 5000).unref();
}
