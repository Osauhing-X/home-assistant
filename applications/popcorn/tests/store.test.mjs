import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { createStore } from '../src/lib/server/popcorn-store.js';

async function fixture(t) {
  const prefix = join(tmpdir(), 'popcorn-test-');
  const directory = await mkdtemp(prefix);
  t.after(async () => {
    assert.ok(resolve(directory).startsWith(resolve(prefix)));
    await rm(directory, { recursive: true, force: true });
  });
  const file = join(directory, 'family.json');
  return { store: createStore(file), file };
}
test('concurrent updates keep every family item', async t => {
  const { store } = await fixture(t);
  await Promise.all(Array.from({ length: 30 }, (_, id) => store.update(data => data.events.push({ id, title: 'Movie ' + id }))));
  assert.equal((await store.read()).events.length, 30);
});
test('saving one unchanged item preserves all other items and folders', async t => {
  const { store } = await fixture(t);
  await store.update(data => { data.events = [{ id: 'a', date: '2026-09-02' }, { id: 'b', date: '2026-10-02' }]; data.folders = [{ id: 'folder' }]; });
  const item = (await store.read()).events[0];
  await store.update(data => { data.events = [item, ...data.events.filter(entry => entry.id !== item.id)]; });
  assert.equal((await store.read()).events.length, 2);
  assert.equal((await store.read()).folders.length, 1);
});
test('corrupt data is not silently replaced with an empty list', async t => {
  const { store, file } = await fixture(t);
  await writeFile(file, '{broken');
  await assert.rejects(store.update(data => data.events.push({ id: 'new' })));
  assert.equal(await readFile(file, 'utf8'), '{broken');
});
test('a failed update does not block later valid saves', async t => {
  const { store } = await fixture(t);
  await assert.rejects(store.update(() => { throw new Error('Rejected'); }));
  await store.update(data => data.events.push({ id: 'ok' }));
  assert.equal((await store.read()).events[0].id, 'ok');
});
