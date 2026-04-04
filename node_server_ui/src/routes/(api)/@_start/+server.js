import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/server/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'Not found' });

  data[name].status = 'running';
  data[name].manual_stop = false;

  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  console.log(`[${name}] marked as running`);

  return json({ ok: true });
}