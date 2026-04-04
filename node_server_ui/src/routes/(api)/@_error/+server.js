// /@_acknowledge_error/+server.js
import fs from 'fs';
import { json } from '@sveltejs/kit';

const STATUS_FILE = '/server/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!name) return json({ error: 'Missing name' });

  const data = fs.existsSync(STATUS_FILE) ? JSON.parse(fs.readFileSync(STATUS_FILE)) : {};
  if (!data[name]) return json({ error: 'Not found' });

  // kustuta error
  data[name].error_message = null;
  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  console.log(`[${name}] error acknowledged by user`);

  return json({ ok: true });
}