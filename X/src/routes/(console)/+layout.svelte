<script>
  import { page } from '$app/stores';
  import { base } from '$app/paths';
  import { onMount } from 'svelte';
  import Shell from '$lib/Shell.svelte';
  let { children } = $props();
  let isConsole=$derived(Boolean($page.route.id?.includes('/(console)/')));
  let active=$derived($page.params.view||$page.route.id?.match(/\(console\)\/([^/]+)/)?.[1]||'dashboard');
  let showDiscover=$state(true);
  onMount(async()=>{try{const response=await fetch(`${base}/api/state`);const state=await response.json();const installed=new Set(state.config.apps.map(app=>app.id));showDiscover=state.config.repositories.some(repo=>(repo.applications||[]).some(app=>!installed.has(app.id)))}catch{}});
</script>

{#if isConsole}<Shell title={active[0].toUpperCase()+active.slice(1)} {active} {showDiscover}>{@render children()}</Shell>{:else}{@render children()}{/if}
