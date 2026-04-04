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
  <div class="node-box">
    <b>{name}</b> — 
    <span class={app.status === 'running' ? 'running' : 'stopped'}>
      {app.status}
    </span>
    {#if app.error}
      <div class="error">
        ⚠ {app.error}
        <button on:click={() => acknowledgeError(name)}>Acknowledge</button>
      </div>
    {/if}

    <div class="controls">
      {#if app.status === 'stopped'}
        <button on:click={() => start(name)} disabled={app.error}>Start</button>
      {:else}
        <button on:click={() => shutdown(name)}>Shutdown</button>
        <button on:click={() => restart(name)}>Restart</button>
        <button on:click={() => update(name)}>Update</button>
      {/if}
    </div>
  </div>
{/each}

<style>
  .node-box {
    background: #111;
    color: #eee;
    padding: 10px;
    margin: 5px 0;
    border-radius: 5px;
  }

  .controls button {
    margin-right: 5px;
    margin-top: 5px;
  }

  .running { color: #0f0; font-weight: bold; }
  .stopped { color: #f55; font-weight: bold; }

  .error {
    color: #f88;
    margin-top: 5px;
    font-size: 0.9em;
  }

  .error button {
    margin-left: 10px;
    background: #f55;
    color: #fff;
    border: none;
    padding: 2px 6px;
    border-radius: 3px;
    cursor: pointer;
  }

  .error button:hover {
    background: #faa;
  }
</style>