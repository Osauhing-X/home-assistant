import { error, json } from '@sveltejs/kit';
import { getConfig, getStatus } from '$lib/server/store.js';

export async function GET({ url, fetch }) {
  const id = url.searchParams.get('id') || '';
  const [config, status] = await Promise.all([getConfig(), getStatus()]);
  const app = config.apps.find((item) => item.id === id);
  if (!app) error(404, 'Application not found.');
  if (status[id]?.state !== 'running') return json({ online: false });
  try {
    const response = await fetch(`http://127.0.0.1:${app.port}/`, { signal: AbortSignal.timeout(1800) });
    return json({ online: response.status < 500 }, { headers: { 'Cache-Control': 'no-store' } });
  } catch {
    return json({ online: false }, { headers: { 'Cache-Control': 'no-store' } });
  }
}
