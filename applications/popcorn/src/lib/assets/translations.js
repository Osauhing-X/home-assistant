import { derived } from 'svelte/store';
import { language } from '$lib/config';

const files = import.meta.glob('./i18n/*.json', { eager: true, import: 'default' });
export const catalogs = Object.fromEntries(Object.entries(files).map(([path, data]) => [path.split('/').pop().slice(0, -5), data]));
export const availableLanguages = Object.keys(catalogs).sort().map(code => ({ code, name: catalogs[code]._meta?.name || new Intl.DisplayNames([code], { type: 'language' }).of(code) }));
export const isLocale = code => Object.hasOwn(catalogs, code);
export const normalizeLocale = code => isLocale(code) ? code : 'en';
export function section(code, key) {
  const fallback = catalogs.en?.[key];
  const value = catalogs[normalizeLocale(code)]?.[key];
  return fallback && typeof fallback === 'object' && !Array.isArray(fallback) ? { ...fallback, ...value } : value ?? fallback;
}
export const t = derived(language, code => (key, values = {}) => {
  const text = section(code, 'messages')?.[key] ?? key;
  return String(text).replace(/\{(\w+)\}/g, (match, name) => Object.hasOwn(values, name) ? String(values[name]) : match);
});
