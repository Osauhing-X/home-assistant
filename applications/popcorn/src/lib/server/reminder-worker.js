import { readStore, updateStore } from './popcorn-store.js';
import { section } from '../assets/translations.js';

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
    if (store.settings?.remindersEnabled === false) return;
    const delivered = [];
    for (const item of store.events || []) {
      if (!item.date || item.date > today() || item.remindedAt) continue;
      const folder = (store.folders || []).find((entry) => entry.id === item.folderId);
      const services = folder?.notifyServices?.length ? folder.notifyServices : (store.settings?.notifyServices || []);
      const labels = section(store.settings.language, 'messages');
      const message = labels['{title} is ready to watch in your Popcorn list.'].replace('{title}', item.title) + (folder?.name ? ` · ${folder.name}` : '');
      await call('/services/persistent_notification/create', { title: '🍿 ' + labels['Popcorn reminder'], message, notification_id: `popcorn_due_${item.id}` });
      for (const service of [...new Set(services)].filter(safeNotify)) {
        try { await call(`/services/notify/${service}`, { title: 'Popcorn', message, data: { tag: `popcorn-due-${item.id}` } }); }
        catch (error) { console.error(`[Popcorn] notify.${service} failed`, error); }
      }
      item.remindedAt = new Date().toISOString();
      delivered.push({ id: item.id, date: item.date, remindedAt: item.remindedAt });
    }
    if (delivered.length) await updateStore((current) => {
      for (const sent of delivered) {
        const entry = current.events.find(item => item.id === sent.id && item.date === sent.date);
        if (entry) entry.remindedAt = sent.remindedAt;
      }
    });
  } catch (error) { console.error('[Popcorn] Reminder check failed', error); }
}

export function startReminderWorker() {
  if (globalThis.__popcornReminderWorker) return;
  globalThis.__popcornReminderWorker = setInterval(checkReminders, 60_000);
  globalThis.__popcornReminderWorker.unref?.();
  checkReminders();
}
