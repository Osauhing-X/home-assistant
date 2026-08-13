import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { error } from '@sveltejs/kit';
import { DATA_DIR, validRepo } from '$lib/server/store.js';

const TYPES = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.svg': 'image/svg+xml' };

export async function GET({ url }) {
  const repository = url.searchParams.get('repository') || '';
  const application = url.searchParams.get('application') || '';
  const asset = url.searchParams.get('path') || '';
  if (!asset || (!application && !validRepo(repository))) error(400, 'Invalid asset request.');
  if (application && !/^[a-z0-9_-]+$/i.test(application)) error(400, 'Invalid application id.');
  const root = application
    ? path.resolve(DATA_DIR, 'applications', application)
    : path.resolve(DATA_DIR, 'repositories', repository.replace('/', '__'));
  const applicationPrefix = `applications/${application}/`;
  const relativeAsset = application && asset.startsWith(applicationPrefix) ? asset.slice(applicationPrefix.length) : asset;
  const file = path.resolve(root, relativeAsset);
  if (!file.startsWith(`${root}${path.sep}`)) error(400, 'Asset path leaves the repository.');
  const type = TYPES[path.extname(file).toLowerCase()];
  if (!type) error(415, 'Unsupported image type.');
  try {
    return new Response(await readFile(file), { headers: { 'Content-Type': type, 'Cache-Control': 'private, max-age=300', 'X-Content-Type-Options': 'nosniff' } });
  } catch { error(404, 'Asset not found.'); }
}
