import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';

const EMPTY = { version: 1, events: [], folders: [], settings: { notifyServices: [] } };
const file = process.env.POPCORN_DATA_FILE || (process.env.SUPERVISOR_TOKEN ? '/data/popcorn-family.json' : join(process.cwd(), '.data', 'popcorn-family.json'));

export async function readStore() {
	try {
		return { ...structuredClone(EMPTY), ...JSON.parse(await readFile(file, 'utf8')) };
	} catch (error) {
		if (error?.code !== 'ENOENT') console.error('[Osaühing X · Popcorn] Store read failed', error);
		return structuredClone(EMPTY);
	}
}

export async function writeStore(data) {
	await mkdir(dirname(file), { recursive: true });
	const temporary = `${file}.tmp`;
	await writeFile(temporary, JSON.stringify(data, null, 2), 'utf8');
	await rename(temporary, file);
	return data;
}

