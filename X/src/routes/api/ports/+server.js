import { json } from '@sveltejs/kit';
import { getConfig, getStatus } from '$lib/server/store.js';
import { portAvailable } from '$lib/server/ports.js';

export async function GET() {
  const [config, status] = await Promise.all([getConfig(), getStatus()]);
  const ports = await Promise.all((config.apps || []).map(async (app) => ({
    appId: app.id,
    name: app.name,
    port: Number(app.port),
    state: status[app.id]?.state || 'stopped',
    listening: !(await portAvailable(Number(app.port)))
  })));
  return json({ ports, allocation: 'X Platform assigns the first free host TCP port, starting at the application preferred port.' });
}
