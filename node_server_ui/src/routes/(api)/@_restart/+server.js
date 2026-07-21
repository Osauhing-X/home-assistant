import { json } from '@sveltejs/kit';
import fs from 'fs';
import { appendLog } from '$lib/server/logger';

const STATUS_FILE = '/data/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!fs.existsSync(STATUS_FILE)) return json({ error: 'No status file' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'Not found' });

  // A distinct state lets the polling watchdog reliably stop the old process.
  data[name].status = 'restarting';
  data[name].error = '';
  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  appendLog(name, 'Restart requested via UI');

  return json({ ok: true });
}
