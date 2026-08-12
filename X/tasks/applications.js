import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { audit, getConfig, tokenFor } from '../src/lib/server/store.js';
import { appDirectory, children, log, redact, setStatus, shell } from './runtime.js';
import { checkout } from './repositories.js';
import { notify } from './notifications.js';

function installEnvironment() {
  const env = { ...process.env };
  for (const key of Object.keys(env)) {
    if (['npm_config_global_style', 'npm_config_install_strategy', 'npm_config_omit', 'npm_config_production', 'node_env'].includes(key.toLowerCase())) delete env[key];
  }
  Object.assign(env, {
    NODE_ENV: 'development',
    NPM_CONFIG_GLOBAL_STYLE: 'false',
    NPM_CONFIG_INSTALL_STRATEGY: 'hoisted',
    NPM_CONFIG_INCLUDE: 'dev',
    NPM_CONFIG_PRODUCTION: 'false',
    NPM_CONFIG_USERCONFIG: '/dev/null'
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
    await checkout(app.repository, app.branch, update);
    const cwd = appDirectory(app);
    const writeLog = (data) => log(app.id, data.trimEnd(), token);
    const env = installEnvironment();
    if (app.install) await shell(app.install, { cwd, env, onData: writeLog });
    if (app.build) await shell(app.build, { cwd, env, onData: writeLog });
    let installedVersion = app.version || 'unknown';
    try { installedVersion = JSON.parse(await readFile(path.join(cwd, 'package.json'), 'utf8')).version || installedVersion; } catch {}
    await setStatus(app.id, { state: 'stopped', installed: true, installedVersion, availableVersion: installedVersion, error: '', recommendation: await detectIntegration(app) });
    if (app.enabled) await startApplication(app);
  } catch (error) {
    await log(app.id, error.message, token);
    await notify('applicationErrors', `Application ${app.name} failed`, error.message);
    await setStatus(app.id, { state: 'error', error: redact(error.message, token) });
  }
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
