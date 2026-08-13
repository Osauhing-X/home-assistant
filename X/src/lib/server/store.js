import { appendFile, mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import path from 'node:path';

export const DATA_DIR = process.env.DATA_DIR || path.resolve('.x-platform-data');
export const CONFIG_FILE = path.join(DATA_DIR, 'platform.json');
export const STATUS_FILE = path.join(DATA_DIR, 'status.json');
export const COMMAND_FILE = path.join(DATA_DIR, 'commands.json');
export const ACTIVE_COMMAND_FILE = path.join(DATA_DIR, 'active-command.json');
export const AUDIT_FILE = path.join(DATA_DIR, 'audit.jsonl');

export const BUILT_INS = [{
  id: 'popcorn',
  name: 'Popcorn',
  description: 'Local movie discovery, watchlists, reminders and movie-night controls.',
  repository: 'Osauhing-X/home-assistant',
  pluginPath: 'applications/popcorn',
  background: 'applications/popcorn/bg.png',
  logo: 'applications/popcorn/logo.png',
  docs: 'README.md',
  port: 8080,
  install: 'npm ci --include=dev --install-strategy=hoisted --no-audit --no-fund',
  build: 'npm run build',
  start: 'node build/index.js',
  envSchema: [
    { name: 'THEMOVIEDB_API', label: 'The Movie Database API key', description: 'API key used to load movie metadata and artwork from TMDB.', secret: true, required: true, example: 'your_tmdb_api_key' },
    { name: 'PASSWORD', label: 'Password', description: 'Optional password required when opening Popcorn. Leave empty to disable login.', secret: true, required: false }
  ],
  homeAssistant: { discovery: true, integration: 'x_entities' }
}];

const DEFAULT_CONFIG = {
  publicHost: '',
  officialRepositoryInitialized: true,
  githubOAuthClientId: '',
  githubAccounts: [],
  repositories: [{
    id: 'osauhing-x__home-assistant',
    fullName: 'Osauhing-X/home-assistant',
    accountId: '', branch: '', env: {}, integrations: [], applications: [],
    scanState: 'queued', official: true
  }],
  apps: [],
  integrations: [],
  updateChecks: { interval: 86400, lastCheck: null },
  notifications: {
    persistentNotification: true,
    notifyServices: [],
    applicationErrors: true,
    applicationStopped: true,
    repositoryErrors: true,
    integrationErrors: true,
    updatesAvailable: false,
    successfulUpdates: false
  },
  installer: {
    enabled: true,
    repositories: ['Osauhing-X/home-assistant'],
    interval: 3600
  }
};

async function json(file, fallback) {
  try { return JSON.parse(await readFile(file, 'utf8')); }
  catch { return structuredClone(fallback); }
}

export async function ensureStore() {
  await mkdir(DATA_DIR, { recursive: true });
  for (const [file, fallback] of [[CONFIG_FILE, DEFAULT_CONFIG], [STATUS_FILE, {}], [COMMAND_FILE, []], [ACTIVE_COMMAND_FILE, null]]) {
    try { await readFile(file); } catch { await atomicWrite(file, fallback); }
  }
}

export async function atomicWrite(file, value) {
  await mkdir(path.dirname(file), { recursive: true });
  const temp = `${file}.${process.pid}.tmp`;
  await writeFile(temp, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  await rename(temp, file);
}

export async function getConfig() {
  await ensureStore();
  const stored = await json(CONFIG_FILE, DEFAULT_CONFIG);
  const migratedAccounts = stored.githubAccounts || (stored.githubToken ? [{ id: 'legacy-pat', login: 'Legacy token', type: 'pat', token: stored.githubToken }] : []);
  return {
    ...DEFAULT_CONFIG,
    ...stored,
    githubAccounts: migratedAccounts,
    repositories: Object.hasOwn(stored, 'officialRepositoryInitialized')
      ? (stored.repositories || [])
      : [...structuredClone(DEFAULT_CONFIG.repositories), ...(stored.repositories || []).filter((item) => item.fullName !== 'Osauhing-X/home-assistant')],
    apps: stored.apps || [],
    integrations: stored.integrations || [],
    updateChecks: { ...DEFAULT_CONFIG.updateChecks, ...(stored.updateChecks || {}) },
    notifications: { ...DEFAULT_CONFIG.notifications, ...(stored.notifications || {}) },
    installer: { ...DEFAULT_CONFIG.installer, ...(stored.installer || {}) }
  };
}

export async function saveConfig(config) {
  await atomicWrite(CONFIG_FILE, { ...DEFAULT_CONFIG, ...config });
}

export async function getStatus() {
  await ensureStore();
  return json(STATUS_FILE, {});
}

export async function enqueue(command) {
  await ensureStore();
  const commands = await json(COMMAND_FILE, []);
  commands.push({ id: randomUUID(), ...command, createdAt: new Date().toISOString() });
  await atomicWrite(COMMAND_FILE, commands);
}

export function publicConfig(config) {
  return {
    ...config,
    githubAccounts: (config.githubAccounts || []).map(({ token, ...account }) => ({ ...account, tokenConfigured: Boolean(token) }))
  };
}

export function tokenFor(config, accountId = '') {
  return (config.githubAccounts || []).find((account) => account.id === accountId)?.token
    || (config.githubAccounts || [])[0]?.token
    || '';
}

export function validRepo(value) {
  return /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(value || '');
}

export function validId(value) {
  return /^[a-z0-9][a-z0-9_-]{1,63}$/.test(value || '');
}

export function bridgeToken() {
  return createHash('sha256').update(`x-platform:${process.env.SUPERVISOR_TOKEN || 'local-development'}`).digest('hex');
}

export async function audit(scope, subject, action, details = '') {
  await ensureStore();
  await appendFile(AUDIT_FILE, `${JSON.stringify({ timestamp: new Date().toISOString(), scope, subject, action, details })}\n`, { mode: 0o600 });
}
