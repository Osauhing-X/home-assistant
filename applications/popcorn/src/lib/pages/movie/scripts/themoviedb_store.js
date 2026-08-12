// $lib/svelte.js THEMOVIEDB
import { writable } from 'svelte/store';

export let list_db = writable({ where:null, data:[], solo:{}, page:1, total:1, fav:{id:[], list:{}}, old:null });
export let urls = writable([
  'https://www.google.com/search?q=[name]', 
  'https://www.youtube.com/results?search_query=[name]'
]);