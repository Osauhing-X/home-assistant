import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { randomUUID } from 'node:crypto';

const EMPTY = { version: 1, events: [], folders: [], settings: { notifyServices: [] } };
export function createStore(file) {
  let pending = Promise.resolve();
  async function read() {
    try {
      const data = JSON.parse(await readFile(file, 'utf8'));
      if (!data || !Array.isArray(data.events) || !Array.isArray(data.folders)) throw new Error('Invalid Popcorn data file; refusing to overwrite it.');
      return { ...structuredClone(EMPTY), ...data, settings: { ...EMPTY.settings, ...data.settings } };
    } catch (error) {
      if (error?.code === 'ENOENT') return structuredClone(EMPTY);
      throw error;
    }
  }
  function update(mutator) {
    const operation = pending.then(async () => {
      const data = await read();
      await mutator(data);
      if (!Array.isArray(data.events) || !Array.isArray(data.folders)) throw new Error('Invalid Popcorn update');
      await mkdir(dirname(file), { recursive: true });
      const temporary = file + '.' + randomUUID() + '.tmp';
      await writeFile(temporary, JSON.stringify(data, null, 2), { encoding: 'utf8', mode: 0o600 });
      await rename(temporary, file);
      return data;
    });
    pending = operation.catch(() => {});
    return operation;
  }
  return { read, update };
}
const storage = createStore(process.env.POPCORN_DATA_FILE || (process.env.SUPERVISOR_TOKEN ? '/data/popcorn-family.json' : join(process.cwd(), '.data', 'popcorn-family.json')));
export const readStore = storage.read;
export const updateStore = storage.update;
