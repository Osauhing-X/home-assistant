import { readFile } from 'node:fs/promises';
import { json } from '@sveltejs/kit';
import { ACTIVE_COMMAND_FILE, COMMAND_FILE, ensureStore } from '$lib/server/store.js';

export async function GET() {
  await ensureStore();
  let active = null;
  let pending = [];
  try { active = JSON.parse(await readFile(ACTIVE_COMMAND_FILE, 'utf8')); } catch {}
  try { pending = JSON.parse(await readFile(COMMAND_FILE, 'utf8')); } catch {}
  return json({ active, pending, count: pending.length + (active ? 1 : 0) }, { headers: { 'Cache-Control': 'no-store, max-age=0' } });
}
