import net from 'node:net';
import { cameras, settings } from './store.js';
import { discoveryRunning } from './discovery.js';
import { relayRunning } from './relay.js';

const cameraStates = new Map();
let lastProbe = 0;

function reachable(camera) {
  return new Promise((resolve) => {
    let url;
    try { url = new URL(camera.hq); } catch { return resolve(false); }
    const socket = net.createConnection({ host: url.hostname, port: Number(url.port || 554) });
    const finish = (value) => { socket.destroy(); resolve(value); };
    socket.setTimeout(1500, () => finish(false));
    socket.once('connect', () => finish(true));
    socket.once('error', () => finish(false));
  });
}

async function notifyOffline(token) {
  const response = await fetch('http://supervisor/core/api/services/persistent_notification/create', {
    method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Camera connection warning', message: 'A configured camera is no longer reachable.', notification_id: 'rtsp_onvif_camera_offline' })
  });
  if (!response.ok) throw new Error(`Home Assistant notification returned HTTP ${response.status}`);
}

async function publish() {
  const token = process.env.SUPERVISOR_TOKEN;
  const host = process.env.X_ENTITIES_HUB_HOST;
  const hubPort = Number(process.env.X_ENTITIES_HUB_PORT || 3099);
  const port = Number(process.env.PORT || 8090);
  if (!token || !host || !process.env.X_APPLICATION_ID) return;
  const [all, config] = await Promise.all([cameras(), settings()]);
  if (Date.now() - lastProbe >= 15_000) {
    const checks = await Promise.all(all.map(async (camera) => [camera, await reachable(camera)]));
    let cameraWentOffline = false;
    for (const [camera, online] of checks) {
      const previous = cameraStates.get(camera.id);
      cameraStates.set(camera.id, online);
      if (previous === true && online === false) cameraWentOffline = true;
    }
    if (config.offlineNotifications !== false && cameraWentOffline) await notifyOffline(token);
    const ids = new Set(all.map((camera) => camera.id));
    for (const id of cameraStates.keys()) if (!ids.has(id)) cameraStates.delete(id);
    lastProbe = Date.now();
  }
  const common = { device: 'RTSP to ONVIF', device_id: 'x_application_rtsp_to_onvif', model: 'X Application', configuration_url: `http://${host}:${port}` };
  const nodeData = {
    heartbeat: { ...common, name: 'Heartbeat', value: true, type: 'binary_sensor', device_class: 'connectivity', icon: 'mdi:heart-pulse' },
    configured_cameras: { ...common, name: 'Configured cameras', value: all.length, type: 'sensor', state_class: 'measurement', icon: 'mdi:cctv' },
    cameras_online: { ...common, name: 'All cameras online', value: all.every((camera) => cameraStates.get(camera.id) === true), type: 'binary_sensor', device_class: 'connectivity', icon: 'mdi:cctv' },
    relay_running: { ...common, name: 'RTSP relay', value: relayRunning(), type: 'binary_sensor', device_class: 'running', icon: 'mdi:video-wireless' },
    discovery_running: { ...common, name: 'ONVIF discovery', value: discoveryRunning(), type: 'binary_sensor', device_class: 'running', icon: 'mdi:radar' },
    offline_notifications: { ...common, name: 'Offline notifications', value: config.offlineNotifications !== false, type: 'switch', icon: 'mdi:bell-alert' }
  };
  const response = await fetch('http://supervisor/core/api/extaas_com', {
    method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ host, port, hub_host: host, hub_port: hubPort, source_id: process.env.X_APPLICATION_ID, node_data: nodeData })
  });
  if (!response.ok) throw new Error(`X Entities returned HTTP ${response.status}: ${(await response.text()).slice(0, 300)}`);
}

export function startXEntitiesPublisher() {
  if (globalThis.__rtspOnvifXEntities) return;
  const run = () => publish().catch((error) => console.warn('[RTSP to ONVIF X Entities]', error.message));
  globalThis.__rtspOnvifXEntities = setInterval(run, 5_000);
  globalThis.__rtspOnvifXEntities.unref?.();
  run();
}
