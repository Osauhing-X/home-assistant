import { getConfig } from '../src/lib/server/store.js';

export async function notify(type, title, message) {
  try {
    const config = await getConfig();
    if (config.notifications?.[type] === false) return;
    await fetch('http://127.0.0.1:3099/api/notify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, message })
    });
  } catch {}
}
