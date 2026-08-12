import { json } from '@sveltejs/kit';
import { randomUUID } from 'node:crypto';
import { readStore, writeStore } from '$lib/server/popcorn-store.js';

const token = process.env.SUPERVISOR_TOKEN;
const core = 'http://supervisor/core/api';
const headers = token ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } : {};
const safeEntity = (value) => /^(light|switch)\.[a-z0-9_]+$/.test(value || '');
const safeNotify = (value) => /^[a-z0-9_]+$/.test(value || '');

async function ha(path, options = {}) {
	if (!token) return null;
	const response = await fetch(`${core}${path}`, { ...options, headers: { ...headers, ...options.headers } });
	if (!response.ok) throw new Error(`Home Assistant ${path}: ${response.status}`);
	return response.status === 204 ? null : response.json();
}

async function inventory() {
	if (!token) return { connected: false, people: [], controls: [], notifyServices: [] };
	try {
		const [states, services] = await Promise.all([ha('/states'), ha('/services')]);
		return {
			connected: true,
			people: states.filter((x) => x.entity_id.startsWith('person.')).map((x) => ({ id: x.entity_id, name: x.attributes?.friendly_name || x.entity_id })),
			controls: states.filter((x) => safeEntity(x.entity_id)).map((x) => ({ id: x.entity_id, name: x.attributes?.friendly_name || x.entity_id, state: x.state })),
			notifyServices: (services.find((x) => x.domain === 'notify')?.services ? Object.keys(services.find((x) => x.domain === 'notify').services) : [])
		};
	} catch (error) {
		console.error('[Osaühing X · Popcorn] HA inventory failed', error);
		return { connected: false, people: [], controls: [], notifyServices: [] };
	}
}

async function notify(item, targets = []) {
	if (!token || !item.date) return;
	const message = `${item.title} · ${item.date}${item.folderName ? ` · ${item.folderName}` : ''}`;
	await ha('/services/persistent_notification/create', { method: 'POST', body: JSON.stringify({ title: '🍿 Popcorn: uus meeldetuletus', message, notification_id: `popcorn_${item.id}` }) });
	for (const service of [...new Set(targets)].filter(safeNotify)) {
		try { await ha(`/services/notify/${service}`, { method: 'POST', body: JSON.stringify({ title: 'Popcorn', message, data: { tag: `popcorn-${item.id}` } }) }); }
		catch (error) { console.error(`[Osaühing X · Popcorn] notify.${service} failed`, error); }
	}
}

export async function GET() {
	return json({ store: await readStore(), ha: await inventory() });
}

export async function POST({ request }) {
	const body = await request.json();
	const store = await readStore();
	if (body.action === 'save') {
		const item = { ...body.item, id: body.item?.id || randomUUID(), createdAt: new Date().toISOString() };
		store.events = [item, ...store.events.filter((x) => x.id !== item.id)];
		await writeStore(store);
		const folder = store.folders.find((x) => x.id === item.folderId);
		await notify({ ...item, folderName: folder?.name }, folder?.notifyServices?.length ? folder.notifyServices : store.settings.notifyServices);
	} else if (body.action === 'remove') {
		store.events = store.events.filter((x) => x.id !== body.id);
		await writeStore(store);
	} else if (body.action === 'folder') {
		const folder = { ...body.folder, id: body.folder?.id || randomUUID() };
		store.folders = [folder, ...store.folders.filter((x) => x.id !== folder.id)];
		await writeStore(store);
	} else if (body.action === 'removeFolder') {
		store.folders = store.folders.filter((x) => x.id !== body.id);
		store.events = store.events.map((x) => x.folderId === body.id ? { ...x, folderId: null } : x);
		await writeStore(store);
	} else if (body.action === 'settings') {
		store.settings = { ...store.settings, ...body.settings };
		await writeStore(store);
	} else if (body.action === 'lightsOff') {
		const folder = store.folders.find((x) => x.id === body.id);
		const entities = (folder?.entities || []).filter(safeEntity);
		for (const domain of ['light', 'switch']) {
			const entity_id = entities.filter((x) => x.startsWith(`${domain}.`));
			if (entity_id.length) await ha(`/services/${domain}/turn_off`, { method: 'POST', body: JSON.stringify({ entity_id }) });
		}
	} else if (body.action === 'toggleEntities') {
		const folder = store.folders.find((x) => x.id === body.id);
		const requested = Array.isArray(body.entities) ? body.entities : (folder?.entities || []);
		const entities = requested.filter((x) => (folder?.entities || []).includes(x) && safeEntity(x));
		for (const domain of ['light', 'switch']) {
			const entity_id = entities.filter((x) => x.startsWith(`${domain}.`));
			if (entity_id.length) await ha(`/services/${domain}/toggle`, { method: 'POST', body: JSON.stringify({ entity_id }) });
		}
	} else if (body.action === 'toggleLocalEntities') {
		const entities = (Array.isArray(body.entities) ? body.entities : []).filter(safeEntity);
		for (const domain of ['light', 'switch']) {
			const entity_id = entities.filter((x) => x.startsWith(`${domain}.`));
			if (entity_id.length) await ha(`/services/${domain}/toggle`, { method: 'POST', body: JSON.stringify({ entity_id }) });
		}
	} else return json({ error: 'Unknown action' }, { status: 400 });
	return json({ store, ha: await inventory() });
}
