import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/data/status.json';

export async function POST({ url }) {
  const name = url.searchParams.get('name');

  if (!fs.existsSync(STATUS_FILE)) {
    return json({ error: 'No status file' });
  }

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));
  if (!data[name]) return json({ error: 'Not found' });

  const pid = data[name].pid;

  if (pid) {
    try {
      // ✅ graceful stop
      process.kill(pid, 'SIGTERM');
      console.log(`[${name}] SIGTERM sent to PID ${pid}`);

      // ✅ fallback force kill
      setTimeout(() => {
        try {
          process.kill(pid, 0); // check if still alive
          process.kill(pid, 'SIGKILL');
          console.log(`[${name}] SIGKILL sent to PID ${pid}`);
        } catch {}
      }, 2000);

    } catch (e) {
      console.log(`[${name}] kill failed (already dead?)`);
    }
  }

  data[name].status = 'stopped';
  data[name].pid = null;

  fs.writeFileSync(STATUS_FILE, JSON.stringify(data));

  return json({ ok: true });
}