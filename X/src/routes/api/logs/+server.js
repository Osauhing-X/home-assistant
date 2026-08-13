import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { error, json } from '@sveltejs/kit';
import { DATA_DIR, validId } from '$lib/server/store.js';

export async function GET({ url }) {
  const id = url.searchParams.get('id') || '';
  if (id !== 'x-installer' && !validId(id)) error(400, 'Invalid application id.');
  try {
    const lines = (await readFile(path.join(DATA_DIR, 'logs', `${id}.log`), 'utf8')).split('\n').slice(-300);
    return json({ lines }, { headers: { 'Cache-Control': 'no-store, max-age=0' } });
  } catch { return json({ lines: [] }, { headers: { 'Cache-Control': 'no-store, max-age=0' } }); }
}

export async function DELETE({ url }) {
  const id = url.searchParams.get('id') || '';
  if (id !== 'x-installer' && !validId(id)) error(400, 'Invalid application id.');
  const directory = path.join(DATA_DIR, 'logs');
  await mkdir(directory, { recursive: true });
  await writeFile(path.join(directory, `${id}.log`), '', { mode: 0o600 });
  return json({ ok: true });
}
