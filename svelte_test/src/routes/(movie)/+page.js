export const prerender = false;

// +page.server.js -> Prerender Error -> new URLSearchParams(url.searchParams)

import meta from './i18n.json'

export function load(){
  return { meta }
}