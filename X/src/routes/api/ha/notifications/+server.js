import { json } from '@sveltejs/kit';

export async function GET({ fetch }) {
  const token = process.env.SUPERVISOR_TOKEN;
  if (!token) return json({ connected: false, notifyServices: [] });
  try {
    const response = await fetch('http://supervisor/core/api/services', { headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) return json({ connected: false, notifyServices: [] });
    const services = await response.json();
    const notify = services.find((item) => item.domain === 'notify');
    return json({ connected: true, notifyServices: notify?.services ? Object.keys(notify.services).sort() : [] });
  } catch {
    return json({ connected: false, notifyServices: [] });
  }
}
