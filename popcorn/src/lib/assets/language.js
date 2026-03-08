/* --- # EXAMPLE
  import json from './language_pack.json'
  import { language } from '$lib/assets/language.js';
  let i18n = get_i18n(json, 'target')

*/


import { writable, readable, get } from 'svelte/store';
import { browser as loaded } from '$app/environment';


// Stores i18n content
  export const i18n = writable()
// Get browser language (auto)
  export const browser = writable((navigator.language || navigator.userLanguage).split('-')[0]);
// The current language that will be displayed on the page
  export const language = writable("en");
// More language options to choose from
  export const available = writable(['en', 'et']);



export function get_i18n(object, target) {
  return readable(get(language), (set) => {
    const unsubscribe = language.subscribe((lang) => {

    // --- # Available languages
      const supported = get(available);

    // --- # Get saved language
      let saved, savedRaw
      if (loaded) savedRaw = localStorage.getItem('save:language');
      if (savedRaw) {
        const fmt = new Intl.DateTimeFormat(savedRaw);
        const resolved = fmt.resolvedOptions().locale.split('-')[0];
        if (resolved === savedRaw) saved = savedRaw; }


    // --- # Determine current language
      let current_lang
        // Kasutaja valitud keel
        = supported.includes(lang) ? lang
        // Kasutaja lemmikuks lisatud keel
        : supported.includes(saved) ? saved
        // Browseri keel ühtib
        : supported.includes(get(browser)) ? get(browser)
        // Fallback - pole ühtegi sobivat
        : 'en'
        // Teeb valitud keele kasutajale nähtavaks
        if(current_lang !== lang) language.set(current_lang);


    // --- # Select data based on format / Markdown
      let selected, data, mdx;
      if(target){ // json format 1 // get_i18n($page.data?.meta?.['demo'], 'demo')
        selected = object?.[target];
        mdx = selected?.mdx;
        data = selected?.[current_lang] ?? {}; }
      else { // json format 2 // get_i18n($page.data?.meta?.['demo'])
        mdx = object?.mdx;
        data = object?.[current_lang] ?? {} }


    // --- # Parse markdown fields / format only if elem is named in array
      (Array.isArray(mdx) ? mdx : []).forEach(k => {
        if (data[k] != null) data[k] = data[k] });


      set(data);
    });

    return unsubscribe;
  });
}


