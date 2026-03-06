/* import { request } from '$lib/assets/i18n/request'
   let i18n = request('fingerprint') */


import { writable, get } from 'svelte/store'

import { page } from '$app/stores'
import { language } from '$lib/config'

import i18n from '$lib/assets/ui.yaml'

export function request(id, data) {
  const store = writable({})

  const update_i18n = () => {
    const lang = get(language) || 'en'
    const found = data ? data[id] : i18n[id]
    store.set(found?.[lang] ?? {})
  }

  const unsub_page = page.subscribe(update_i18n)
  const unsub_lang = language.subscribe(update_i18n)

  update_i18n()

  return {
    subscribe: store.subscribe,
    destroy() {
      unsub_page()
      unsub_lang()
    }
  }
}