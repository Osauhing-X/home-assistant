import { readStore } from './popcorn-store.js';

const intervalMs = 5_000;
const today = () => new Intl.DateTimeFormat('sv-SE', { timeZone: process.env.TZ || 'Europe/Tallinn' }).format(new Date());

async function publish() {
  const token = process.env.SUPERVISOR_TOKEN;
  const host = process.env.X_ENTITIES_HUB_HOST;
  const hubPort = Number(process.env.X_ENTITIES_HUB_PORT || 3099);
  const port = Number(process.env.PORT || 8080);
  if (!token || !host || !process.env.X_APPLICATION_ID) return;
  const store = await readStore();
  const events = store.events || [];
  const common = { device: 'Popcorn', device_id: 'x_application_popcorn', model: 'X Application', configuration_url: `http://${host}:${port}` };
  const nodeData = {
    heartbeat: { ...common, name: 'Heartbeat', value: true, type: 'binary_sensor', device_class: 'connectivity', icon: 'mdi:heart-pulse' },
    watchlist_count: { ...common, name: 'Saved titles', value: events.length, type: 'sensor', state_class: 'measurement', icon: 'mdi:movie-open' },
    upcoming_reminders: { ...common, name: 'Upcoming reminders', value: events.filter((item) => item.date && item.date >= today() && !item.remindedAt).length, type: 'sensor', state_class: 'measurement', icon: 'mdi:calendar-clock' },
    folder_count: { ...common, name: 'Folders', value: (store.folders || []).length, type: 'sensor', state_class: 'measurement', icon: 'mdi:folder-multiple' },
    reminders_enabled: { ...common, name: 'Reminders', value: store.settings?.remindersEnabled !== false, type: 'switch', icon: 'mdi:bell' }
  };
  const response = await fetch('http://supervisor/core/api/extaas_com', {
    method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ host, port, hub_host: host, hub_port: hubPort, hub_service: 'X Platform', source_id: process.env.X_APPLICATION_ID, node_data: nodeData })
  });
  if (!response.ok) throw new Error(`X Entities returned HTTP ${response.status}: ${(await response.text()).slice(0, 300)}`);
}

export function startXEntitiesPublisher() {
  if (globalThis.__popcornXEntities) return;
  const run = () => publish().catch((error) => console.warn('[Popcorn X Entities]', error.message));
  globalThis.__popcornXEntities = setInterval(run, intervalMs);
  globalThis.__popcornXEntities.unref?.();
  run();
}
