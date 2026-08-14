import { json } from '@sveltejs/kit';
import { readStore, writeStore } from '$lib/server/popcorn-store.js';

export async function POST({ request }) {
  const updates = await request.json();
  if (Object.hasOwn(updates, 'reminders_enabled')) {
    const store = await readStore();
    store.settings = { ...store.settings, remindersEnabled: Boolean(updates.reminders_enabled) };
    await writeStore(store);
  }
  return json({ ok: true });
}
