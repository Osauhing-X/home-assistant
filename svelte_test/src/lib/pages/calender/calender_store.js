import { writable } from 'svelte/store';

export let calender = writable([])
export let selected = writable([])
export let selectedYM = writable({ year: new Date().getFullYear(), month: new Date().getMonth() })