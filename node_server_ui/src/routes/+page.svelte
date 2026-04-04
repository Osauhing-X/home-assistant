<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths';

  let apps = {};

  async function load() {
    const res = await fetch(base + '/@_get');
    apps = await res.json();
  }

  async function start(name) { await fetch(base + `/@_start?name=${name}`, { method: 'POST' }); load(); }
  async function shutdown(name) { await fetch(base + `/@_shutdown?name=${name}`, { method: 'POST' }); load(); }
  async function restart(name) { await fetch(base + `/@_restart?name=${name}`, { method: 'POST' }); load(); }
  async function update(name) { await fetch(base + `/@_update?name=${name}`, { method: 'POST' }); load(); }

  onMount(load);
</script>

<h1>Node Apps</h1>

{#each Object.entries(apps) as [name, app]}
  <div>
    <b>{name}</b> — {app.status} 
    {#if app.status === 'stopped'}
      <button on:click={() => start(name)}>Start</button>
    {:else}
      <button on:click={() => shutdown(name)}>Shutdown</button>
      <button on:click={() => restart(name)}>Restart</button>
      <button on:click={() => update(name)}>Update</button>
    {/if}
    <label>
      <input type="checkbox" bind:checked={app.boot_on_start} on:change={async () => {
        await fetch(base + `/@_boot?name=${name}&boot_on_start=${app.boot_on_start}`, { method: 'POST' });
        load();
      }}> Boot on start
    </label>
  </div>
{/each}

<style>
  div { background: black; color: #aaa; padding: 5px; margin: 2px; }
  button { margin: 2px; }
</style>