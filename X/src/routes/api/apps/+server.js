import { error, json } from '@sveltejs/kit';
import { BUILT_INS, enqueue, getConfig, saveConfig, validId, validRepo } from '$lib/server/store.js';
import { allocatePort } from '$lib/server/ports.js';

export async function POST({ request }) {
  const input = await request.json();
  const configureOnly = input.configureOnly === true;
  const builtIn = BUILT_INS.find((item) => item.id === input.catalogId);
  const source = builtIn ? { ...builtIn } : input;
  const baseId = String(source.sourceId || source.id || source.repository?.split('/').pop() || '').toLowerCase().replace(/[^a-z0-9_-]/g, '-');
  if (!validId(baseId)) error(400, 'Invalid application id.');
  if (!validRepo(source.repository)) error(400, 'Repository must use owner/name format.');
  const missingEnvironment = (source.envSchema || []).filter((item) => item.required && !String(source.env?.[item.name] || '').trim()).map((item) => item.name);
  if (!configureOnly && missingEnvironment.length) error(400, `Required environment variables are missing: ${missingEnvironment.join(', ')}.`);

  const config = await getConfig();
  let id = baseId, instance = 1;
  while (config.apps.some((app) => app.id === id)) id = `${baseId}-${++instance}`;
  const port = await allocatePort(config, source.port);
  const app = {
    id,
    sourceId: baseId,
    instance,
    name: `${source.name || baseId}${instance > 1 ? ` ${instance}` : ''}`,
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
    logo: source.logo || '',
    background: source.background || '',
    docs: source.docs || '',
    gui: source.gui !== false,
    homeAssistant: source.homeAssistant || { discovery: false },
    updatePolicy: source.updatePolicy || 'manual',
    enabled: !configureOnly
  };
  config.apps.push(app);
  if (!config.repositories.some((repo) => repo.fullName === app.repository)) config.repositories.push({ fullName: app.repository, env: {} });
  await saveConfig(config);
  if (!configureOnly) await enqueue({ type: 'install', appId: id });
  return json({ ok: true, app }, { status: 201 });
}

export async function PUT({ request }) {
  const input = await request.json();
  const config = await getConfig();
  const index = config.apps.findIndex((app) => app.id === input.id);
  if (index < 0) error(404, 'Application not found.');
  const port = input.installPending ? await allocatePort(config, config.apps[index].port, config.apps[index].id) : config.apps[index].port;
  const { installPending = false, saveOnly = false, ...updates } = input;
  if (installPending) updates.enabled = true;
  config.apps[index] = { ...config.apps[index], ...updates, id: config.apps[index].id, port };
  if (installPending || !saveOnly) {
    const missingEnvironment = (config.apps[index].envSchema || []).filter((item) => item.required && !String(config.apps[index].env?.[item.name] || '').trim()).map((item) => item.name);
    if (missingEnvironment.length) error(400, `Required environment variables are missing: ${missingEnvironment.join(', ')}.`);
  }
  await saveConfig(config);
  if (!saveOnly && installPending) await enqueue({ type: 'install', appId: input.id });
  return json({ ok: true });
}
