<script>
	let { children } = $props();

	import '$lib/assets/build.css'
	import '$lib/assets/global.css'

	import { page } from '$app/stores';
	import { base } from '$app/paths';
</script>

{@render children()}

<button on:click={()=>console.log('dev : ', $page, '👍', base)}></button
