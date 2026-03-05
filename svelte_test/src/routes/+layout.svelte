<script>
	let { children } = $props();

	import '$lib/assets/build.css'
	import '$lib/assets/global.css'

	import { page } from '$app/stores';
	import { base } from '$app/paths';

	console.log('dev 1:',$page)
	console.log('dev 2:',base)
</script>

{@render children()}


