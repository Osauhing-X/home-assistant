import { json } from '@sveltejs/kit';
import { saveSettings, settings } from '$lib/server/store.js';

export async function POST({ request }) {
  const updates = await request.json();
  if (Object.hasOwn(updates, 'offline_notifications')) {
    await saveSettings({ ...await settings(), offlineNotifications: Boolean(updates.offline_notifications) });
  }
  return json({ ok: true });
}
