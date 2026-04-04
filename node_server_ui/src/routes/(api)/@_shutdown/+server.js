import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/server/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'Not found' });

  // kill olemasolev PID
  if (data[name].pid) {
    try { process.kill(data[name].pid); } catch(e) {}
  }

  data[name].status = 'stopped';
  data[name].pid = null;
  data[name].manual_stop = true;

  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  console.log(`[${name}] stopped by user`);

  return json({ ok: true });
}