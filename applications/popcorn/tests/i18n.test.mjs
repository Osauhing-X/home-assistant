import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
const root = new URL('../src/', import.meta.url);
const en = JSON.parse(readFileSync(new URL('lib/assets/i18n/en.json', root)));
const et = JSON.parse(readFileSync(new URL('lib/assets/i18n/et.json', root)));
function keys(value, prefix = '') {
  return Object.entries(value).flatMap(([key, child]) => child && typeof child === 'object' ? keys(child, prefix + key + '.') : [prefix + key]).sort();
}
test('English and Estonian catalogs contain the same translation keys', () => {
  assert.deepEqual(keys(en), keys(et));
});
function files(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const url = new URL(entry.name + (entry.isDirectory() ? '/' : ''), directory);
    return entry.isDirectory() ? files(url) : [url];
  });
}
test('every literal portal translation reference exists in both catalogs', () => {
  for (const file of files(root).filter(url => url.pathname.endsWith('.svelte'))) {
    const source = readFileSync(file, 'utf8');
    for (const match of source.matchAll(/\$t\(\s*(['"])(.*?)\1/g)) {
      assert.ok(Object.hasOwn(en.messages, match[2]), file.pathname + ': ' + match[2]);
      assert.ok(Object.hasOwn(et.messages, match[2]), file.pathname + ': ' + match[2]);
    }
  }
});
