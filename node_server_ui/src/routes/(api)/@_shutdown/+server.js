import { json } from '@sveltejs/kit';
import fs from 'fs';
const STATUS_FILE = '/server/status.json';
export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!name) return json({ error: 'Missing name' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  const app = data[name];
  if (!app) return json({ error: 'App not found' });

  // SHUTDOWN = peatame node
  if (app.status === 'running') {
    try { process.kill(app.pid); } catch(e) {}
    app.status = 'stopped';
    fs.writeFileSync(STATUS_FILE, JSON.stringify(data));
    console.log(`[${name}] shutdown`);
  }

  return json({ ok: true });
}