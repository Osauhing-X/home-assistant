import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { createHash, randomBytes, randomUUID } from 'node:crypto';
import path from 'node:path';

export const DATA_DIR = process.env.DATA_DIR || path.resolve('.x-platform-data');
export const CONFIG_FILE = path.join(DATA_DIR, 'platform.json');
export const STATUS_FILE = path.join(DATA_DIR, 'status.json');
export const COMMAND_FILE = path.join(DATA_DIR, 'commands.json');
export const ACTIVE_COMMAND_FILE = path.join(DATA_DIR, 'active-command.json');
export const AUDIT_FILE = path.join(DATA_DIR, 'audit.jsonl');
export const INSTALLATION_ID_FILE = path.join(DATA_DIR, 'installation-identity');
const AUDIT_LIMIT=100;
let auditQueue=Promise.resolve();
let communityCache={expires:0,repositories:[]};

// Applications are discovered from repositories. Keeping a second built-in
// manifest here would duplicate package.json and x_config.json metadata.
export const BUILT_INS = [];

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
  const temp = `${file}.${process.pid}.${randomUUID()}.tmp`;
  await writeFile(temp, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  await rename(temp, file);
}

export async function getConfig() {
  await ensureStore();
  const stored = await json(CONFIG_FILE, DEFAULT_CONFIG);
  const migratedAccounts = stored.githubAccounts || (stored.githubToken ? [{ id: 'legacy-pat', login: 'Legacy token', type: 'pat', token: stored.githubToken }] : []);
  const communityRepositories=await getCommunityRepositories();
  const repositories=Object.hasOwn(stored, 'officialRepositoryInitialized')
    ? (stored.repositories || [])
    : [...structuredClone(DEFAULT_CONFIG.repositories), ...(stored.repositories || []).filter((item) => item.fullName !== 'Osauhing-X/home-assistant')];
  for(const repository of repositories){
    repository.official=isOfficialRepository(repository.fullName);
    repository.community=communityRepositories.includes(normalizeRepository(repository.fullName));
  }
  for(const fullName of communityRepositories){
    if(repositories.some((repository)=>normalizeRepository(repository.fullName)===fullName))continue;
    const canonical=fullName.split('/').map((part)=>part).join('/');
    repositories.push({
      id:canonical.replace('/','__').toLowerCase(),fullName:canonical,
      accountId:'',branch:'',env:{},integrations:[],applications:[],
      scanState:'queued',official:isOfficialRepository(canonical),community:true
    });
  }
  return {
    ...DEFAULT_CONFIG,
    ...stored,
    githubAccounts: migratedAccounts,
    repositories,
    apps: stored.apps || [],
    integrations: stored.integrations || [],
    updateChecks: { ...DEFAULT_CONFIG.updateChecks, ...(stored.updateChecks || {}) },
    notifications: { ...DEFAULT_CONFIG.notifications, ...(stored.notifications || {}) },
    installer: { ...DEFAULT_CONFIG.installer, ...(stored.installer || {}) }
  };
}

export function normalizeRepository(value='') {
  return String(value).trim().replace(/^https?:\/\/github\.com\//i,'').replace(/\.git\/?$/i,'').replace(/^\/+|\/+$/g,'').toLowerCase();
}

export function isOfficialRepository(value='') {
  return normalizeRepository(value).startsWith('osauhing-x/');
}

async function getCommunityRepositories() {
  if(communityCache.expires>Date.now())return communityCache.repositories;
  const candidates=[
    process.env.X_COMMUNITY_FILE,
    path.resolve(process.cwd(),'..','community.yaml'),
    path.join(DATA_DIR,'repositories','Osauhing-X__home-assistant','community.yaml')
  ].filter(Boolean);
  let content='';
  for(const file of candidates){try{content=await readFile(file,'utf8');if(content)break}catch{}}
  const yaml=content.split(/\r?\n/).filter((line)=>!line.trimStart().startsWith('#')).join('\n');
  const repositories=[...new Set([...yaml.matchAll(/https?:\/\/github\.com\/([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)(?:\.git)?/gi)].map((match)=>normalizeRepository(match[1])))];
  communityCache={expires:Date.now()+30000,repositories};
  return repositories;
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

export async function installationIdentity() {
  await ensureStore();
  try {
    const value = (await readFile(INSTALLATION_ID_FILE, 'utf8')).trim();
    if (value) return value;
  } catch {}
  const value = randomBytes(32).toString('base64url');
  await writeFile(INSTALLATION_ID_FILE, `${value}\n`, { mode: 0o600, flag: 'wx' }).catch(() => {});
  return (await readFile(INSTALLATION_ID_FILE, 'utf8')).trim();
}

export async function audit(scope, subject, action, details = '') {
  await ensureStore();
  const entry=JSON.stringify({timestamp:new Date().toISOString(),scope,subject,action,details});
  auditQueue=auditQueue.catch(()=>{}).then(async()=>{let lines=[];try{lines=(await readFile(AUDIT_FILE,'utf8')).split(/\r?\n/).filter(Boolean)}catch{}lines.push(entry);lines=lines.slice(-AUDIT_LIMIT);await writeFile(AUDIT_FILE,`${lines.join('\n')}\n`,{mode:0o600})});
  await auditQueue;
}
