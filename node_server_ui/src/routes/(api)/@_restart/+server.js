import { json } from '@sveltejs/kit';
import fs from 'fs';
import { appendLog } from '$lib/server/logger';

const STATUS_FILE = '/data/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!fs.existsSync(STATUS_FILE)) return json({ error: 'No status file' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'Not found' });

  // Stop first
  data[name].status = 'stopped';
  data[name].error = '';
  appendLog(name, 'Stopping for restart');
  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  // Mark running (watchdog käivitab)
  data[name].status = 'running';
  appendLog(name, 'Starting after restart');
  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  return json({ ok: true });
}