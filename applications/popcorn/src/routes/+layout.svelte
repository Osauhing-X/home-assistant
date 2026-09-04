<script>
	let { children } = $props();
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { language } from '$lib/config';
	import { normalizeLocale } from '$lib/assets/translations';
	onMount(() => language.set(normalizeLocale($page.params.lang || $page.url.searchParams.get('language') || localStorage.getItem('popcorn:language'))));

	import '$lib/assets/style/build.css'
	import '$lib/assets/style/global.css'
	import '$lib/assets/style/portal.css'
	import '$lib/assets/style/enhancements.css'
</script>

{@render children()}
