import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { error } from '@sveltejs/kit';
import { DATA_DIR, validRepo } from '$lib/server/store.js';

const TYPES = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.svg': 'image/svg+xml' };

export async function GET({ url }) {
  const repository = url.searchParams.get('repository') || '';
  const asset = url.searchParams.get('path') || '';
  if (!validRepo(repository) || !asset) error(400, 'Invalid asset request.');
  const root = path.resolve(DATA_DIR, 'repositories', repository.replace('/', '__'));
  const file = path.resolve(root, asset);
  if (!file.startsWith(`${root}${path.sep}`)) error(400, 'Asset path leaves the repository.');
  const type = TYPES[path.extname(file).toLowerCase()];
  if (!type) error(415, 'Unsupported image type.');
  try {
    return new Response(await readFile(file), { headers: { 'Content-Type': type, 'Cache-Control': 'private, max-age=300', 'X-Content-Type-Options': 'nosniff' } });
  } catch { error(404, 'Asset not found.'); }
}
