import express from 'express';
import bonjourFactory from 'bonjour';
import os from 'node:os';
import { bridgeToken, enqueue, getConfig, getStatus } from './src/lib/server/store.js';

const PORT = Number(process.env.X_BRIDGE_PORT || 3099);
const DOMAIN = 'extaas_com';
const SERVICE = 'X Platform';
const app = express();
app.use(express.json({ limit: '1mb' }));
const requireApplication = (request, response, next) => request.get('x-x-platform-token') === bridgeToken() ? next() : response.status(401).json({ error: 'invalid application token' });

export function getLocalIp() { let fallback;
  for (const [name, addresses] of Object.entries(os.networkInterfaces()))
    for (const address of addresses || [])
      if (address.family === 'IPv4' && !address.internal && !/^(lo|docker|veth|br-|hassio|vmnet|vboxnet)/i.test(name))
        if (/^(en|eth|wlan|wl)/i.test(name)) return address.address; else fallback ??= address.address;
  return fallback || '127.0.0.1';
}

const hostIp = getLocalIp();
let haUrl = process.env.HA_URL || null;
const bonjour = bonjourFactory();

bonjour.publish({ host: hostIp, name: SERVICE, port: PORT, type: DOMAIN, txt: { data: JSON.stringify({ integration: DOMAIN, hostname: os.hostname(), service_name: SERVICE, model: 'X Plugin Platform' }) } });
bonjour.find({ type: 'home-assistant' }).on('up', (service) => {
  const ipv4 = service.addresses?.find((address) => address.includes('.'));
  if (ipv4) haUrl = `http://${ipv4}:${service.port}`;
});

app.get('/heartbeat', (_request, response) => response.status(200).send('OK'));
app.post('/update', async (request, response) => {
  const config = await getConfig();
  for (const [key, value] of Object.entries(request.body || {})) {
    const match = /^application_(.+)_power$/.exec(key);
    if (!match) continue;
    const application = config.apps.find((item) => item.id === match[1]);
    if (application) await enqueue({ type: value ? 'start' : 'stop', appId: application.id });
  }
  response.json({ ok: true });
});

app.post('/api/notify', async (request, response) => {
  const title = String(request.body?.title || 'X Platform').slice(0, 100);
  const message = String(request.body?.message || '').slice(0, 4000);
  if (!message) return response.status(400).json({ error: 'message is required' });
  try { await notifyHomeAssistant(title, message); response.json({ ok: true }); }
  catch (error) { response.status(502).json({ error: error.message }); }
});

app.get('/api/ha/states', requireApplication, async (_request, response) => proxyHa(response, '/states'));
app.get('/api/ha/states/:entity', requireApplication, async (request, response) => proxyHa(response, `/states/${encodeURIComponent(request.params.entity)}`));
app.post('/api/ha/services/:domain/:service', requireApplication, async (request, response) => {
  if (!/^[a-z0-9_]+$/.test(request.params.domain) || !/^[a-z0-9_]+$/.test(request.params.service)) return response.status(400).json({ error: 'invalid service' });
  return proxyHa(response, `/services/${request.params.domain}/${request.params.service}`, request.body);
});

async function proxyHa(response, path, body) {
  const token = process.env.SUPERVISOR_TOKEN;
  if (!token) return response.status(503).json({ error: 'Home Assistant API unavailable' });
  try {
    const result = await fetch(`http://supervisor/core/api${path}`, { method: body === undefined ? 'GET' : 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, ...(body === undefined ? {} : { body: JSON.stringify(body) }) });
    const text = await result.text(); response.status(result.status).type(result.headers.get('content-type') || 'application/json').send(text);
  } catch (error) { response.status(502).json({ error: error.message }); }
}

async function notifyHomeAssistant(title, message) {
  const token = process.env.SUPERVISOR_TOKEN;
  if (!token) throw new Error('SUPERVISOR_TOKEN is unavailable');
  const config = await getConfig();
  const call = async (path, body) => {
    const result = await fetch(`http://supervisor/core/api${path}`, { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (!result.ok) throw new Error(`Home Assistant returned ${result.status} for ${path}`);
  };
  const jobs = [];
  if (config.notifications?.persistentNotification !== false) jobs.push(call('/services/persistent_notification/create', { title, message, notification_id: `x_platform_${Date.now()}` }));
  for (const service of [...new Set(config.notifications?.notifyServices || [])].filter((value) => /^[a-z0-9_]+$/.test(value))) {
    jobs.push(call(`/services/notify/${service}`, { title, message, data: { tag: `x-platform-${Date.now()}` } }));
  }
  if (!jobs.length) return;
  const results = await Promise.allSettled(jobs);
  const failed = results.filter((item) => item.status === 'rejected');
  if (failed.length === results.length) throw failed[0].reason;
}

async function nodeData() {
  const config = await getConfig();
  const status = await getStatus();
  const running = config.apps.filter((item) => status[item.id]?.state === 'running').length;
  const errors = config.apps.filter((item) => status[item.id]?.state === 'error').length;
  const data = {
    platform_health: { name: 'X status', value: errors ? 'error' : 'running', type: 'sensor', icon: errors ? 'mdi:alert-circle' : 'mdi:check-circle', device: SERVICE },
    running_applications: { name: 'Running applications', value: running, type: 'sensor', icon: 'mdi:application', state_class: 'measurement', device: SERVICE },
    managed_integrations: { name: 'Managed integrations', value: config.integrations.length, type: 'sensor', icon: 'mdi:puzzle', state_class: 'measurement', device: SERVICE }
  };
  for (const application of config.apps.filter((item) => status[item.id]?.installed)) {
    const common = {
      device: `${SERVICE} ${application.name}`,
      device_id: `x_platform_application_${application.id}`,
      model: 'X Application',
      via_device: 'x_platform',
      ...(application.gui === false ? {} : { configuration_url: `http://${hostIp}:${application.port}` })
    };
    data[`application_${application.id}_status`] = { ...common, name: 'Status', value: status[application.id]?.state || 'stopped', type: 'sensor', icon: 'mdi:application-cog' };
    data[`application_${application.id}_power`] = { ...common, name: 'Running', value: status[application.id]?.state === 'running', type: 'switch', icon: 'mdi:power' };
  }
  return data;
}

async function syncEntities() {
  if (!haUrl) return;
  try { await fetch(`${haUrl}/api/${DOMAIN}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ host: hostIp, port: PORT, node_data: await nodeData() }) }); }
  catch (error) { console.error('[X HA Bridge]', error.message); }
}

app.listen(PORT, '0.0.0.0', () => console.log(`[X HA Bridge] ${hostIp}:${PORT}`));
setInterval(syncEntities, 5000);
syncEntities();
