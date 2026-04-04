import { json } from '@sveltejs/kit';
import fs from 'fs';
import { exec } from 'child_process';

const STATUS_FILE = '/server/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!name) return json({ error: 'Missing name' });

  const DIR = `/server/app_${name}`;
  exec(`cd ${DIR} && git pull --rebase && npm install --omit=dev`);

  return json({ ok: true });
}