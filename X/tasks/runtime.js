import { spawn } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { atomicWrite, DATA_DIR, STATUS_FILE } from '../src/lib/server/store.js';

export const REPOSITORIES_DIR = path.join(DATA_DIR, 'repositories');
export const LOGS_DIR = path.join(DATA_DIR, 'logs');
export const INTEGRATIONS_DIR = path.join(DATA_DIR, 'integrations');
export const APPLICATIONS_DIR = path.join(DATA_DIR, 'applications');
export const HA_COMPONENTS_DIR = process.env.HA_COMPONENTS_DIR || '/homeassistant/custom_components';
export const children = new Map();
export let status = {};
const TERMINAL_LINE_LIMIT=1000,logQueues=new Map(),COMMAND_OUTPUT_LIMIT=256*1024;

export function localIp() {
  let fallback = '';
  for (const [name, addresses] of Object.entries(os.networkInterfaces())) {
    for (const address of addresses || []) {
      if (address.family !== 'IPv4' || address.internal || /^(lo|docker|veth|br-|hassio|vmnet|vboxnet)/i.test(name)) continue;
      if (/^(en|eth|wlan|wl)/i.test(name)) return address.address;
      fallback ||= address.address;
    }
  }
  return fallback || '127.0.0.1';
}

export async function initializeRuntime() {
  await Promise.all([
    mkdir(REPOSITORIES_DIR, { recursive: true }),
    mkdir(LOGS_DIR, { recursive: true }),
    mkdir(INTEGRATIONS_DIR, { recursive: true })
    ,mkdir(APPLICATIONS_DIR, { recursive: true })
  ]);
  try { status = JSON.parse(await readFile(STATUS_FILE, 'utf8')); } catch { status = {}; }
}

export function repoDirectory(repository) {
  return path.join(REPOSITORIES_DIR, repository.replace('/', '__'));
}

export function appDirectory(app) {
  return path.join(APPLICATIONS_DIR, app.id);
}

export function appSourceDirectory(app) {
  const root = path.resolve(repoDirectory(app.repository));
  const selected = path.resolve(root, app.pluginPath || '.');
  if (selected !== root && !selected.startsWith(`${root}${path.sep}`)) throw new Error('Plugin path leaves the repository.');
  return selected;
}

export function appVersionCopyDirectory(app) {
  return path.join(appDirectory(app), 'version_copy');
}

export function redact(message, token) {
  return token ? String(message).split(token).join('[secret]') : String(message);
}

export async function log(id, message, token = '') {
  const safe=redact(message,token),stamp=new Date().toISOString(),incoming=String(safe).split(/\r?\n/).map(line=>`[${stamp}] ${line}`),file=path.join(LOGS_DIR,`${id}.log`);
  const queued=(logQueues.get(id)||Promise.resolve()).catch(()=>{}).then(async()=>{await mkdir(LOGS_DIR,{recursive:true});let existing=[];try{existing=(await readFile(file,'utf8')).split(/\r?\n/).filter(Boolean)}catch{}const lines=[...existing,...incoming].slice(-TERMINAL_LINE_LIMIT);await writeFile(file,`${lines.join('\n')}${lines.length?'\n':''}`,{mode:0o600})});
  logQueues.set(id,queued);await queued;
  console.log(`[${id}] ${safe}`);
}

export async function clearLog(id) {
  const queued=(logQueues.get(id)||Promise.resolve()).catch(()=>{}).then(async()=>{await mkdir(LOGS_DIR,{recursive:true});await writeFile(path.join(LOGS_DIR,`${id}.log`),'',{mode:0o600})});logQueues.set(id,queued);await queued;
}

export async function setStatus(id, patch) {
  status[id] = { state: 'stopped', ...status[id], ...patch, updatedAt: new Date().toISOString() };
  await atomicWrite(STATUS_FILE, status);
}

export async function removeStatus(id) {
  delete status[id];
  await atomicWrite(STATUS_FILE, status);
}

export function shell(command, options = {}) {
  return new Promise((resolve, reject) => {
    const { timeoutMs = 0, idleSuccessMs = 0, ...spawnOptions } = options;
    const child = spawn('/bin/sh', ['-lc', `exec ${command}`], { ...spawnOptions, stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '';
    let settled = false;
    let idleTimer = null;
    const finishIdle = () => {
      if (settled) return;
      settled = true;
      child.kill('SIGTERM');
      if (timer) clearTimeout(timer);
      resolve(output);
    };
    const resetIdle = () => {
      if (!idleSuccessMs || settled) return;
      if (idleTimer) clearTimeout(idleTimer);
      idleTimer = setTimeout(finishIdle, idleSuccessMs);
      idleTimer.unref();
    };
    const timer = timeoutMs ? setTimeout(() => {
      if (settled) return;
      settled = true;
      child.kill('SIGKILL');
      reject(new Error(`Command timed out after ${Math.round(timeoutMs / 1000)} seconds: ${command}`));
    }, timeoutMs) : null;
    timer?.unref();
    const capture=(data)=>{output=(output+data).slice(-COMMAND_OUTPUT_LIMIT);options.onData?.(data.toString());resetIdle()};
    child.stdout.on('data', capture);
    child.stderr.on('data', capture);
    child.once('error', (error) => { if (!settled) { settled = true; if (timer) clearTimeout(timer); if (idleTimer) clearTimeout(idleTimer); reject(error); } });
    child.once('exit', (code) => {
      if (settled) return;
      settled = true;
      if (timer) clearTimeout(timer);
      if (idleTimer) clearTimeout(idleTimer);
      if (code === 0) return resolve(output);
      const limit = 3500;
      const details = output.length <= limit ? output : `${output.slice(0, 1800)}\n\n[... output truncated ...]\n\n${output.slice(-1700)}`;
      reject(new Error(`Command exited with ${code}: ${details}`));
    });
    resetIdle();
  });
}

export function stopChildren() {
  for (const child of children.values()) child.kill('SIGTERM');
}
