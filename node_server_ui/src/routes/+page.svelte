<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths';

  let apps = {};

  async function load() {
    const res = await fetch(base + '/@_get');
    apps = await res.json();
  }

  async function start(name) {
    await fetch(base + `/@_start?name=${name}`, { method: 'POST' });
    load();
  }

  async function shutdown(name) {
    await fetch(base + `/@_shutdown?name=${name}`, { method: 'POST' });
    load();
  }

  async function restart(name) {
    await fetch(base + `/@_restart?name=${name}`, { method: 'POST' });
    load();
  }

  async function update(name) {
    await fetch(base + `/@_update?name=${name}`, { method: 'POST' });
    load();
  }

  async function acknowledgeError(name) {
    await fetch(base + `/@_error?name=${name}`, { method: 'POST' });
    load();
  }

  onMount(load);
</script>

<h1>Node Apps</h1>

{#each Object.entries(apps) as [name, app]}
  <div>
    <b>{name}</b> — {app.status} (v{app.version})
    {#if app.error_message !== null}
      <div style="color: red;">Error: {app.error_message}</div>
      <button on:click={() => acknowledgeError(name)}>Acknowledge Error & Enable Start</button>
    {/if}
    {#if app.status === 'stopped'}
      <button on:click={() => start(name)} disabled={app.error_message !== null}>Start</button>
    {:else}
      <button on:click={() => shutdown(name)}>Shutdown</button>
      <button on:click={() => restart(name)}>Restart</button>
      <button on:click={() => update(name)}>Update</button>
    {/if}
  </div>
{/each}

<style>
  div { background: black; color: #aaa; padding: 8px; margin: 5px; border-radius: 5px; }
  button { margin: 3px; }
</style>