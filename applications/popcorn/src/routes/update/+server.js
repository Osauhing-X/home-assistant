import { json } from '@sveltejs/kit';
import { updateStore } from '$lib/server/popcorn-store.js';

export async function POST({ request }) {
  const updates = await request.json();
  if (Object.hasOwn(updates, 'reminders_enabled')) {
    await updateStore((store) => {
    store.settings = { ...store.settings, remindersEnabled: Boolean(updates.reminders_enabled) };
    });
  }
  return json({ ok: true });
}
