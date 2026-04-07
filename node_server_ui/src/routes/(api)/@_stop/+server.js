import { json } from '@sveltejs/kit';
import fs from 'fs';
import { appendLog } from '$lib/server/logger';

const STATUS_FILE = '/data/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!fs.existsSync(STATUS_FILE)) return json({ error: 'No status file' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'Not found' });

  // Node peatamine toimub watchdog kaudu
  data[name].status = 'stopped';  // Node watchdog peatab protsessi
  data[name].error = '';
  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  appendLog(name, 'Shutdown requested via UI');

  return json({ ok: true });
}