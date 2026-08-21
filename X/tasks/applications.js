import { spawn } from 'node:child_process';
import { cp, mkdir, readFile, rename, rm, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { audit, DATA_DIR, getConfig, installationIdentity, saveConfig, tokenFor } from '../src/lib/server/store.js';
import { appDirectory, appSourceDirectory, appVersionCopyDirectory, children, localIp, log, redact, removeStatus, setStatus, shell, status } from './runtime.js';
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

async function dependenciesMatch(left, right) {
  const fingerprint = async (directory) => {
    const packageJson = JSON.parse(await readFile(path.join(directory, 'package.json'), 'utf8'));
    const dependencies = {
      dependencies: packageJson.dependencies || {}, devDependencies: packageJson.devDependencies || {},
      optionalDependencies: packageJson.optionalDependencies || {}, peerDependencies: packageJson.peerDependencies || {}
    };
    let lock = null;
    for (const file of ['package-lock.json', 'npm-shrinkwrap.json']) {
      try {
        lock = JSON.parse(await readFile(path.join(directory, file), 'utf8'));
        if (lock.packages?.['']) { delete lock.packages[''].name; delete lock.packages[''].version; }
        delete lock.name;
        delete lock.version;
        break;
      } catch {}
    }
    return JSON.stringify({ dependencies, lock });
  };
  try { return await fingerprint(left) === await fingerprint(right); }
  catch { return false; }
}

export async function installApplication(app, update = false, skipInstall = false) {
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
    let pendingLogWrites = Promise.resolve();
    const writeLog = (data) => {
      const message = data.trimEnd();
      if (message) pendingLogWrites = pendingLogWrites.then(() => log(app.id, message, token));
      return pendingLogWrites;
    };
    const env = await installEnvironment();
    const installCommand = app.install?.trim() === 'npm ci'
      ? 'npm install --include=dev --install-strategy=hoisted'
      : app.install;
    if (installCommand && !skipInstall) {
      await log(app.id, 'Update phase: installing dependencies.');
      await shell(installCommand, { cwd, env, onData: writeLog, timeoutMs: 10 * 60 * 1000 });
      await pendingLogWrites;
    }
    else if (skipInstall) await log(app.id, 'Dependencies unchanged; reused existing node_modules.');
    if (app.build) {
      await log(app.id, 'Update phase: building application.');
      await shell(app.build, { cwd, env, onData: writeLog, timeoutMs: 15 * 60 * 1000, idleSuccessMs: 180 * 1000 });
      await pendingLogWrites;
    }
    let installedVersion = app.version || '';
    if (!installedVersion) {
      try { installedVersion = JSON.parse(await readFile(path.join(cwd, 'package.json'), 'utf8')).version || ''; } catch {}
    }
    installedVersion ||= 'unknown';
    await setStatus(app.id, { state: app.enabled ? (update ? 'updating' : 'installing') : 'stopped', installed: true, installedVersion, availableVersion: installedVersion, updateAvailable: false, error: '', recommendation: await detectIntegration(app) });
    await log(app.id, `${update ? 'Update' : 'Installation'} code prepared (${installedVersion}).`);
    if (app.enabled) {
      await log(app.id, 'Update phase: starting application.');
      await startApplication(app, { pendingState: update ? 'updating' : 'installing' });
    }
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
  const heldVersion = `${active}.version-copy.next`;
  await rm(temporary, { recursive: true, force: true });
  await rm(heldVersion, { recursive: true, force: true });
  await log(app.id, 'Update phase: swapping staged code.');
  const reuseDependencies = await dependenciesMatch(active, staged);
  await rename(staged, heldVersion);
  await cp(heldVersion, temporary, { recursive: true });
  if (reuseDependencies) {
    try { await rename(path.join(active, 'node_modules'), path.join(temporary, 'node_modules')); } catch {}
  }
  await rm(active, { recursive: true, force: true });
  await rename(temporary, active);
  await rename(heldVersion, appVersionCopyDirectory(app));
  await installApplication(app, true, reuseDependencies);
}

export async function deleteApplication(app) {
  await stopApplication(app);
  for (let attempt = 0; attempt < 12 && children.has(app.id); attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  await rm(appDirectory(app), { recursive: true, force: true });
  const config = await getConfig();
  config.apps = config.apps.filter((item) => item.id !== app.id);
  await saveConfig(config);
  await removeStatus(app.id);
  await audit('application', app.id, 'deleted');
}

export async function startApplication(app, { pendingState = '' } = {}) {
  if (children.has(app.id)) return;
  const directory = appDirectory(app);
  const config = await getConfig();
  const repository = config.repositories.find((item) => item.fullName === app.repository);
  const configuredHost = String(config.publicHost || '').trim().replace(/^https?:\/\//, '').replace(/\/.*$/, '').replace(/:\d+$/, '');
  const installationId = await installationIdentity();
  const applicationDataDirectory = path.join(DATA_DIR, 'application-data', app.id);
  await mkdir(applicationDataDirectory, { recursive: true });
  const env = {
    ...process.env, ...(repository?.env || {}), ...(app.env || {}),
    HOST: '0.0.0.0', PORT: String(app.port),
    ORIGIN: `http://${configuredHost || localIp()}:${app.port}`,
    X_PLATFORM: 'true',
    X_APPLICATION_ID: app.id,
    X_INSTALLATION_ID: installationId,
    X_APPLICATION_DATA_DIR: applicationDataDirectory,
    X_ENTITIES_HUB_HOST: localIp(),
    X_ENTITIES_HUB_PORT: String(process.env.X_BRIDGE_PORT || 3099)
  };
  const child = spawn('/bin/sh', ['-lc', `exec ${app.start}`], { cwd: directory, env, stdio: ['ignore', 'pipe', 'pipe'], detached: false });
  children.set(app.id, child);
  await setStatus(app.id, { state: pendingState || 'running', pid: child.pid, error: '', port: app.port });
  let ready = !pendingState;
  const output = async (data) => {
    const text = data.toString().trimEnd();
    await log(app.id, text);
    if (!ready && /(listening on|server running|local:\s*http|started server)/i.test(text)) {
      ready = true;
      await setStatus(app.id, { state: 'running', error: '', pid: child.pid, port: app.port });
      await log(app.id, 'Application ready.');
    }
  };
  child.stdout.on('data', output);
  child.stderr.on('data', output);
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
  const exited = new Promise((resolve) => child.once('exit', resolve));
  child.kill('SIGTERM');
  await audit('application', app.id, 'stopped');
  let forceTimer;
  const forced = new Promise((resolve) => {
    forceTimer = setTimeout(() => {
      if (children.has(app.id)) child.kill('SIGKILL');
      resolve();
    }, 5000);
    forceTimer.unref();
  });
  await Promise.race([exited, forced]);
  clearTimeout(forceTimer);
  for (let attempt = 0; attempt < 10 && children.has(app.id); attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  await setStatus(app.id, { state: 'stopped', pid: null });
}
