// Osaühing X · Popcorn local reminder worker
import { readFile, writeFile } from 'node:fs/promises';

const file = process.env.POPCORN_DATA_FILE || '/data/popcorn-family.json';
const token = process.env.SUPERVISOR_TOKEN;
const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
const today = () => new Intl.DateTimeFormat('sv-SE', { timeZone: process.env.TZ || 'Europe/Tallinn' }).format(new Date());

async function call(path, body) {
	if (!token) return;
	const response = await fetch(`http://supervisor/core/api${path}`, { method: 'POST', headers, body: JSON.stringify(body) });
	if (!response.ok) throw new Error(`${path}: ${response.status}`);
}

async function check() {
	try {
		const store = JSON.parse(await readFile(file, 'utf8'));
		let changed = false;
		for (const item of store.events || []) {
			if (!item.date || item.date > today() || item.remindedAt) continue;
			const folder = (store.folders || []).find((x) => x.id === item.folderId);
			const services = folder?.notifyServices?.length ? folder.notifyServices : (store.settings?.notifyServices || []);
			const message = `${item.title} on nüüd sinu Popcorni nimekirjas vaatamiseks valmis${folder?.name ? ` · ${folder.name}` : ''}.`;
			await call('/services/persistent_notification/create', { title: '🍿 Popcorni meeldetuletus', message, notification_id: `popcorn_due_${item.id}` });
			for (const service of [...new Set(services)].filter((x) => /^[a-z0-9_]+$/.test(x))) {
				try { await call(`/services/notify/${service}`, { title: 'Popcorn', message, data: { tag: `popcorn-due-${item.id}` } }); } catch (error) { console.error(error); }
			}
			item.remindedAt = new Date().toISOString(); changed = true;
		}
		if (changed) await writeFile(file, JSON.stringify(store, null, 2), 'utf8');
	} catch (error) {
		if (error?.code !== 'ENOENT') console.error('[Osaühing X · Popcorn] Reminder check failed', error);
	}
}

await check();
setInterval(check, 60_000);

