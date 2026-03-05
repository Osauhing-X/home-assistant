<script>
	import { base } from '$app/paths';

	let { children } = $props();

	import '$lib/assets/build.css'
	import '$lib/assets/global.css'
</script>


<svelte:head>
	<base href={base}>
</svelte:head>


{@render children()}


