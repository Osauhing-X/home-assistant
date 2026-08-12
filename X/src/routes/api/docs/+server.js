import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { error, json } from '@sveltejs/kit';
import { DATA_DIR, getConfig } from '$lib/server/store.js';

export async function GET({ url }) {
  const id = url.searchParams.get('id') || '';
  const type = url.searchParams.get('type') === 'integration' ? 'integration' : 'application';
  if (!/^[a-zA-Z0-9_.-]+(?:--[a-zA-Z0-9_.-]+)?$/.test(id)) error(400, 'Invalid id.');
  const config = await getConfig();
  const repositoryName = url.searchParams.get('repository');
  const item = type === 'integration' ? config.integrations.find((entry) => entry.id === id) : config.apps.find((entry) => entry.id === id) || config.repositories.find((repo) => repo.fullName === repositoryName)?.applications?.find((entry) => entry.id === id);
  if (!item) error(404, 'Item not found.');
  const repository = item.repository || repositoryName;
  const root = path.resolve(DATA_DIR, 'repositories', repository.replace('/', '__'), item.pluginPath || item.path || '.');
  const file = path.resolve(root, item.docs || 'README.md');
  if (file !== root && !file.startsWith(`${root}${path.sep}`)) error(400, 'Documentation path leaves the item.');
  try { return json({ available: true, content: await readFile(file, 'utf8') }); }
  catch { return json({ available: false, content: '' }); }
}
