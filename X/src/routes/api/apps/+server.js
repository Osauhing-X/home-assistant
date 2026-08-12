import { error, json } from '@sveltejs/kit';
import { BUILT_INS, enqueue, getConfig, saveConfig, validId, validRepo } from '$lib/server/store.js';

export async function POST({ request }) {
  const input = await request.json();
  const builtIn = BUILT_INS.find((item) => item.id === input.catalogId);
  const source = builtIn ? { ...builtIn } : input;
  const id = String(source.id || source.repository?.split('/').pop() || '').toLowerCase().replace(/[^a-z0-9_-]/g, '-');
  if (!validId(id)) error(400, 'Invalid application id.');
  if (!validRepo(source.repository)) error(400, 'Repository must use owner/name format.');
  const port = Number(source.port);
  if (!Number.isInteger(port) || port < 1024 || port > 65535) error(400, 'Port must be between 1024 and 65535.');

  const config = await getConfig();
  if (config.apps.some((app) => app.id === id)) error(409, `Application id "${id}" is already in use.`);
  if (config.apps.some((app) => app.port === port)) error(409, `Port ${port} is already in use by another application.`);
  const app = {
    id,
    name: source.name || id,
    description: source.description || '',
    repository: source.repository,
    pluginPath: source.pluginPath || '.',
    branch: source.branch || '',
    port,
    install: source.install || 'npm install',
    build: source.build || '',
    start: source.start || 'node index.js',
    env: source.env || {},
    envSchema: source.envSchema || [],
    icon: source.icon || '',
    background: source.background || '',
    docs: source.docs || '',
    gui: source.gui !== false,
    homeAssistant: source.homeAssistant || { discovery: false },
    updatePolicy: source.updatePolicy || 'manual',
    enabled: true
  };
  config.apps.push(app);
  if (!config.repositories.some((repo) => repo.fullName === app.repository)) config.repositories.push({ fullName: app.repository, env: {} });
  await saveConfig(config);
  await enqueue({ type: 'install', appId: id });
  return json({ ok: true, app }, { status: 201 });
}

export async function PUT({ request }) {
  const input = await request.json();
  const config = await getConfig();
  const index = config.apps.findIndex((app) => app.id === input.id);
  if (index < 0) error(404, 'Application not found.');
  const port = Number(input.port ?? config.apps[index].port);
  if (!Number.isInteger(port) || port < 1024 || port > 65535) error(400, 'Invalid port.');
  if (config.apps.some((app, i) => i !== index && app.port === port)) error(409, 'Port is already in use.');
  const { installPending = false, ...updates } = input;
  config.apps[index] = { ...config.apps[index], ...updates, id: config.apps[index].id, port };
  await saveConfig(config);
  await enqueue({ type: installPending ? 'install' : 'restart', appId: input.id });
  return json({ ok: true });
}
