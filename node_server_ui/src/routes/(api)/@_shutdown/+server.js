import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/server/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!name) return json({ error: 'Missing name' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'App not found' });

  if (data[name].status === 'running') {
    try { process.kill(data[name].pid); } catch(e) {}
    data[name].status = 'stopped';
    data[name].pid = null;
    fs.writeFileSync(STATUS_FILE, JSON.stringify(data));
  }

  return json({ ok: true });
}