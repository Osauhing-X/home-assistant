import { readStore, writeStore } from './popcorn-store.js';

const token = process.env.SUPERVISOR_TOKEN;
const core = 'http://supervisor/core/api';
const safeNotify = (value) => /^[a-z0-9_]+$/.test(value || '');
const today = () => new Intl.DateTimeFormat('sv-SE', { timeZone: process.env.TZ || 'Europe/Tallinn' }).format(new Date());

async function call(path, body) {
  if (!token) return;
  const response = await fetch(`${core}${path}`, { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!response.ok) throw new Error(`Home Assistant ${path}: ${response.status}`);
}

async function checkReminders() {
  if (!token) return;
  try {
    const store = await readStore();
    let changed = false;
    for (const item of store.events || []) {
      if (!item.date || item.date > today() || item.remindedAt) continue;
      const folder = (store.folders || []).find((entry) => entry.id === item.folderId);
      const services = folder?.notifyServices?.length ? folder.notifyServices : (store.settings?.notifyServices || []);
      const message = `${item.title} on nüüd sinu Popcorni nimekirjas vaatamiseks valmis${folder?.name ? ` · ${folder.name}` : ''}.`;
      await call('/services/persistent_notification/create', { title: '🍿 Popcorni meeldetuletus', message, notification_id: `popcorn_due_${item.id}` });
      for (const service of [...new Set(services)].filter(safeNotify)) {
        try { await call(`/services/notify/${service}`, { title: 'Popcorn', message, data: { tag: `popcorn-due-${item.id}` } }); }
        catch (error) { console.error(`[Popcorn] notify.${service} failed`, error); }
      }
      item.remindedAt = new Date().toISOString();
      changed = true;
    }
    if (changed) await writeStore(store);
  } catch (error) { console.error('[Popcorn] Reminder check failed', error); }
}

export function startReminderWorker() {
  if (globalThis.__popcornReminderWorker) return;
  globalThis.__popcornReminderWorker = setInterval(checkReminders, 60_000);
  globalThis.__popcornReminderWorker.unref?.();
  checkReminders();
}
