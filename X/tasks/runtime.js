import { spawn } from 'node:child_process';
import { appendFile, mkdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { atomicWrite, DATA_DIR, STATUS_FILE } from '../src/lib/server/store.js';

export const REPOSITORIES_DIR = path.join(DATA_DIR, 'repositories');
export const LOGS_DIR = path.join(DATA_DIR, 'logs');
export const INTEGRATIONS_DIR = path.join(DATA_DIR, 'integrations');
export const HA_COMPONENTS_DIR = process.env.HA_COMPONENTS_DIR || '/homeassistant/custom_components';
export const children = new Map();
export let status = {};

export async function initializeRuntime() {
  await Promise.all([
    mkdir(REPOSITORIES_DIR, { recursive: true }),
    mkdir(LOGS_DIR, { recursive: true }),
    mkdir(INTEGRATIONS_DIR, { recursive: true })
  ]);
  try { status = JSON.parse(await readFile(STATUS_FILE, 'utf8')); } catch { status = {}; }
}

export function repoDirectory(repository) {
  return path.join(REPOSITORIES_DIR, repository.replace('/', '__'));
}

export function appDirectory(app) {
  const root = path.resolve(repoDirectory(app.repository));
  const selected = path.resolve(root, app.pluginPath || '.');
  if (selected !== root && !selected.startsWith(`${root}${path.sep}`)) throw new Error('Plugin path leaves the repository.');
  return selected;
}

export function redact(message, token) {
  return token ? String(message).split(token).join('[secret]') : String(message);
}

export async function log(id, message, token = '') {
  const line = `[${new Date().toISOString()}] ${redact(message, token)}`;
  await appendFile(path.join(LOGS_DIR, `${id}.log`), `${line}\n`);
  console.log(`[${id}] ${redact(message, token)}`);
}

export async function setStatus(id, patch) {
  status[id] = { state: 'stopped', ...status[id], ...patch, updatedAt: new Date().toISOString() };
  await atomicWrite(STATUS_FILE, status);
}

export function shell(command, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn('/bin/sh', ['-lc', command], { ...options, stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '';
    child.stdout.on('data', (data) => { output += data; options.onData?.(data.toString()); });
    child.stderr.on('data', (data) => { output += data; options.onData?.(data.toString()); });
    child.once('error', reject);
    child.once('exit', (code) => code === 0 ? resolve(output) : reject(new Error(`Command exited with ${code}: ${output.slice(-2000)}`)));
  });
}

export function stopChildren() {
  for (const child of children.values()) child.kill('SIGTERM');
}
