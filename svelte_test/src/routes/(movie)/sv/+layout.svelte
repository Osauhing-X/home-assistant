<script>
	import { page } from '$app/stores';
	import { base } from '$lib/config.js'

	$: sv_path = $page.url.href?.split('/sv');
	$: $base = sv_path[0] + '/sv/' ;
</script>


<svelte:head>
	<base href={$base}>
</svelte:head>


<slot />
