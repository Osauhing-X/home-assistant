import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/server/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  const value = url.searchParams.get('boot_on_start') === 'true';

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));

  if (!data[name]) return json({ error: 'Not found' });

  data[name].boot_on_start = value;

  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  return json({ ok: true });
}