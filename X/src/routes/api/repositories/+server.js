import { error, json } from '@sveltejs/kit';
import { audit, enqueue, getConfig, saveConfig, validRepo } from '$lib/server/store.js';

export async function POST({ request }) {
  const input = await request.json();
  if (!validRepo(input.fullName)) error(400, 'Invalid repository.');
  const config = await getConfig();
  const existing = config.repositories.find((repo) => repo.fullName === input.fullName);
  if (!existing) config.repositories.push({
    id: input.fullName.replace('/', '__').toLowerCase(), fullName: input.fullName,
    accountId: input.accountId || '', branch: input.branch || '', env: {},
    integrations: [], applications: [], scanState: 'queued'
  });
  await saveConfig(config);
  await enqueue({ type: 'scan-repository', repository: input.fullName });
  await audit('repository', input.fullName, existing ? 'rescan_requested' : 'added');
  return json({ ok: true }, { status: existing ? 200 : 201 });
}

export async function PUT({ request }) {
  const input = await request.json();
  if (!validRepo(input.fullName)) error(400, 'Invalid repository.');
  const config = await getConfig();
  const existing = config.repositories.find((repo) => repo.fullName === input.fullName);
  const env = Object.fromEntries(Object.entries(input.env || {}).filter(([key]) => /^[A-Za-z_][A-Za-z0-9_]*$/.test(key)));
  if (existing) existing.env = env;
  else config.repositories.push({ fullName: input.fullName, env });
  await saveConfig(config);
  await audit('repository', input.fullName, 'settings_changed', input.rescan ? 'rescan requested' : 'environment changed');
  if (input.rescan) await enqueue({ type: 'scan-repository', repository: input.fullName });
  return json({ ok: true });
}

export async function DELETE({ request }) {
  const input = await request.json();
  if (!validRepo(input.fullName)) error(400, 'Invalid repository.');
  const config = await getConfig();
  config.repositories = config.repositories.filter((repo) => repo.fullName !== input.fullName);
  await saveConfig(config);
  await audit('repository', input.fullName, 'removed');
  return json({ ok: true });
}
