<script>
  import { page } from '$app/stores';
  import Shell from '$lib/Shell.svelte';
  let { children } = $props();
  let isConsole=$derived(Boolean($page.route.id?.includes('/(console)/')));
  let active=$derived($page.params.view||$page.route.id?.match(/\(console\)\/([^/]+)/)?.[1]||'dashboard');
</script>

{#if isConsole}<Shell title={active[0].toUpperCase()+active.slice(1)} {active}>{@render children()}</Shell>{:else}{@render children()}{/if}
