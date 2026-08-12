import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { error, json } from '@sveltejs/kit';
import { DATA_DIR, getConfig, validId } from '$lib/server/store.js';

export async function GET({ url }) {
  const id = url.searchParams.get('id') || '';
  if (!validId(id)) error(400, 'Invalid application id.');
  const config = await getConfig();
  const app = config.apps.find((item) => item.id === id);
  if (!app) error(404, 'Application not found.');
  const root = path.resolve(DATA_DIR, 'repositories', app.repository.replace('/', '__'), app.pluginPath || '.');
  const file = path.resolve(root, app.docs || 'README.md');
  if (!file.startsWith(`${root}${path.sep}`)) error(400, 'Documentation path leaves the application.');
  try { return json({ available: true, content: await readFile(file, 'utf8') }); }
  catch { return json({ available: false, content: '' }); }
}
