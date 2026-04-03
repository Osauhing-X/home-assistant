import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/server/status.json';

export async function GET() {
  if (!fs.existsSync(STATUS_FILE)) return json({});
  const data = JSON.parse(fs.readFileSync(STATUS_FILE));
  return json(data);
}

export async function POST({ url }) {
  const params = url.searchParams;
  const name = params.get('name');
  const action = params.get('action');

  if (!name || !action) return json({ error: 'Missing parameters' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));

  const app = data[name];
  if (!app) return json({ error: 'App not found' });

  if (action === 'restart') {
    process.kill(app.pid);
    data[name].status = 'restarting';
    fs.writeFileSync(STATUS_FILE, JSON.stringify(data));
  }

  if (action === 'pull') {
    const { exec } = await import('child_process');
    exec(`cd /server/app_${name} && git pull --rebase && npm install --omit=dev`);
  }

  return json({ ok: true });
}