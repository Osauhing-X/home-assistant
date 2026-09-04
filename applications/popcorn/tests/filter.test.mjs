import test from 'node:test';
import assert from 'node:assert/strict';
import { filterSaved } from '../src/lib/assets/saved-list.js';
const items = [{ id:'a', title:'Alpha', date:'2026-09-02', folderId:'f' }, { id:'b', title:'Beta', date:'2026-10-01' }, { id:'c', title:'Gamma', date:'' }];
test('month filtering includes matching folder entries without changing saved data', () => {
  assert.deepEqual(filterSaved(items,'','az','2026-09',[]).map(x=>x.id), ['a']);
  assert.equal(items.length, 3);
});
test('clearing the month restores dated and undated entries', () => {
  assert.equal(filterSaved(items,'','az','',[]).length, 3);
});
test('folder search does not mutate source order', () => {
  assert.deepEqual(filterSaved(items,'family','za','',[{id:'f',name:'Family'}]).map(x=>x.id), ['a']);
  assert.deepEqual(items.map(x=>x.id), ['a','b','c']);
});
