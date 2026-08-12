import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { error, json } from '@sveltejs/kit';
import { DATA_DIR, validId } from '$lib/server/store.js';

export async function GET({ url }) {
  const id = url.searchParams.get('id') || '';
  if (id !== 'x-installer' && !validId(id)) error(400, 'Invalid application id.');
  try {
    const lines = (await readFile(path.join(DATA_DIR, 'logs', `${id}.log`), 'utf8')).split('\n').slice(-300);
    return json({ lines });
  } catch { return json({ lines: [] }); }
}

