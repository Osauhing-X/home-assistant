import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/server/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  const keepAliveStr = url.searchParams.get('keep_alive');
  const keep_alive = keepAliveStr === 'true';

  const data = JSON.parse(fs.readFileSync(STATUS_FILE));

  if (!data[name]) return json({ error: 'Not found' });

  data[name].keep_alive = keep_alive;

  fs.writeFileSync(STATUS_FILE, JSON.stringify(data, null, 2));

  console.log(`[${name}] keep_alive set to ${keep_alive}`);

  return json({ ok: true });
}