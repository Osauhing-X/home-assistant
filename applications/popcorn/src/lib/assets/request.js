import { derived } from 'svelte/store';
import { language } from '$lib/config';
import { section } from './translations.js';

export function request(id) {
  return derived(language, code => section(code, id) ?? {});
}
