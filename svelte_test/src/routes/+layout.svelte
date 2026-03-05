<script>
	import { page } from '$app/stores';
	import { base } from '$lib/config.js'

	import '$lib/assets/build.css'
	import '$lib/assets/global.css'

	

	$: $base = ($page.url.href.split('/sv/'))[0] + "/sv/";
</script>

<svelte:head>
	<base href={$base}>
</svelte:head>

<slot />

