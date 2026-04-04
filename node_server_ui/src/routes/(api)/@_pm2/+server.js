import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/data/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  const keep_alive = url.searchParams.get('keep_alive') === 'true';
  if (!fs.existsSync(STATUS_FILE)) return json({ error: 'No status file' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'Not found' });

  data[name].keep_alive = keep_alive;
  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));
  return json({ ok: true });
}