import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/server/status.json';


export async function POST({ url }) {
  const name = url.searchParams.get('name');

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  const app = data[name];

  if (!app) return json({ error: 'Not found' });

  try {
    process.kill(app.pid);
  } catch {}

  data[name].enabled = false;
  data[name].status = 'stopped';

  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  return json({ ok: true });
}