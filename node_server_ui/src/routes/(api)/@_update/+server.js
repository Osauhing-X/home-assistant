// node_server_ui/src/routes/api/update/+server.js
import { json } from '@sveltejs/kit';
import fs from 'fs';
import { spawn } from 'child_process';

const STATUS_FILE = '/server/status.json';

export async function POST({ url }) {
  // Võta query params
  const name = url.searchParams.get('name');
  if (!name) return json({ error: 'Missing name' });

  // Lae status fail
  if (!fs.existsSync(STATUS_FILE)) return json({ error: 'Status file not found' });
  let data = JSON.parse(fs.readFileSync(STATUS_FILE));

  const app = data[name];
  if (!app) return json({ error: 'App not found' });

  // Node kausta tee
  const dir = `/server/app_${name}`;

  console.log(`[${name}] starting update (git pull + npm install)`);

  // Käivita git pull + npm install spawn-iga, et logid terminalis näha
  const child = spawn('bash', ['-c', 'git pull --rebase && npm install --omit=dev'], {
    cwd: dir,
    stdio: 'inherit'  // logid terminali
  });

  // Kui update lõpetab
  child.on('exit', (code) => {
    console.log(`[${name}] update finished with exit code ${code}`);
    // Status jääb samaks, ei muudeta
  });

  // Tagasta kohe response, ei pea ootama update lõppu
  return json({ ok: true, message: 'Update started, check logs for progress' });
}