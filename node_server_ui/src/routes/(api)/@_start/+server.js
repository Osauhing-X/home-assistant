import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/server/status.json';


export async function POST({ url }) {
  const name = url.searchParams.get('name');

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));

  if (!data[name]) data[name] = {};

  data[name].enabled = true;
  data[name].status = 'starting';

  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  return json({ ok: true });
}