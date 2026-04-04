import { json } from '@sveltejs/kit';
import fs from 'fs';
import { spawn } from 'child_process';

const STATUS_FILE = '/data/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!name) return json({ error: 'Missing name' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'App not found' });

  const DIR = `/server/app_${name}`;

  console.log(`[${name}] Restarting...`);

  // Kill olemasolev PID (stop)
  if (data[name].pid) {
    try { process.kill(data[name].pid); } catch(e) {}
    data[name].status = 'stopped';
    data[name].pid = null;
  }

  // Start uuesti spawn-iga, et logid näha
  const child = spawn('node', ['index.js'], {
    cwd: DIR,
    detached: true,
    stdio: 'inherit'
  });

  data[name].pid = child.pid;
  data[name].status = 'running';
  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  console.log(`[${name}] Restarted with PID ${child.pid}`);

  return json({ ok: true });
}