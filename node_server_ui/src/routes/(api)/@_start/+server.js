import { json } from '@sveltejs/kit';
import fs from 'fs';
import { exec } from 'child_process';

const STATUS_FILE = '/server/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!name) return json({ error: 'Missing name' });

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'App not found' });

  if (data[name].status === 'stopped') {
    const DIR = `/server/app_${name}`;
    const child = exec(`cd ${DIR} && node index.js`);
    data[name].pid = child.pid;
    data[name].status = 'running';
    fs.writeFileSync(STATUS_FILE, JSON.stringify(data));
  }

  return json({ ok: true });
}