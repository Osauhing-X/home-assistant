import { json } from '@sveltejs/kit';
import fs from 'fs';
const STATUS_FILE = '/server/status.json';
export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!name) return json({ error: 'Missing name' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  const app = data[name];
  if (!app) return json({ error: 'App not found' });

  // START = käivitame node kui see ei tööta
  if (app.status !== 'running') {
    const { spawn } = await import('child_process');
    const dir = `/server/app_${name}`;
    const child = spawn('node', ['index.js'], { cwd: dir, stdio: 'inherit' });
    app.pid = child.pid;
    app.status = 'running';
    fs.writeFileSync(STATUS_FILE, JSON.stringify(data));
    console.log(`[${name}] started with PID ${child.pid}`);
  }

  return json({ ok: true });
}