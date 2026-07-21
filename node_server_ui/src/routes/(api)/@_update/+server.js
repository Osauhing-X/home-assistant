/*
  UI (Svelte)
   ↓ fetch POST /@_update?name=ha-server
  API endpoint (+server.js)
   ↓ spawn("git pull && npm install")
  Node process (child_process)
   ↓ muudab faile diskil
  Watchdog (bash)
   ↓ EI TEE MIDAGI automaatselt
*/

import { json } from '@sveltejs/kit';
import fs from 'fs';
import { spawn } from 'child_process';
import { appendLog } from '$lib/server/logger';

export async function POST({ url }) {
  const name = url.searchParams.get('name');
  if (!name) return json({ error: 'Missing name' }, { status: 400 });
  if (!/^[a-zA-Z0-9._-]+$/.test(name)) {
    return json({ error: 'Invalid application name' }, { status: 400 });
  }

  const dir = `/server/app_${name}`;
  if (!fs.existsSync(dir)) {
    return json({ error: 'Application not found' }, { status: 404 });
  }

  appendLog(name, 'Starting update (git pull + npm install)');

  const child = spawn('bash', ['-c', 'git pull --rebase && npm install'], {
    cwd: dir
  });

  child.stdout.on('data', (data) => {
    appendLog(name, data.toString().trim());
  });

  child.stderr.on('data', (data) => {
    appendLog(name, `[ERROR] ${data.toString().trim()}`);
  });

  child.on('error', (error) => {
    appendLog(name, `[ERROR] Update could not start: ${error.message}`);
  });

  child.on('exit', (code) => {
    appendLog(name, `Update finished with exit code ${code}`);
  });

  return json({ ok: true });
}
