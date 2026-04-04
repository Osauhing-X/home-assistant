<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths';
  import { browser } from '$app/environment';

  let apps = {};

  // --- Load node info ---
  async function load() {
    if (!browser) return;
    try {
      const res = await fetch(base + '/@_get');
      apps = await res.json();
    } catch(e) {
      console.error('Failed to load apps', e);
    }
  }

  async function start(name) {
    await fetch(base + `/@_start?name=${name}`, { method: 'POST' });
    await load();
  }

  async function shutdown(name) {
    await fetch(base + `/@_stop?name=${name}`, { method: 'POST' });
    await load();
  }

  async function restart(name) {
    await fetch(base + `/@_restart?name=${name}`, { method: 'POST' });
    await load();
  }

  async function update(name) {
    await fetch(base + `/@_update?name=${name}`, { method: 'POST' });
    await load();
  }

  async function acknowledgeError(name) {
    await fetch(base + `/@_error?name=${name}`, { method: 'POST' });
    await load();
  }

  async function toggleKeepAlive(name, value) {
    await fetch(base + `/@_pm2?name=${name}&keep_alive=${value}`, { method: 'POST' });
    await load();
  }

  // --- Auto refresh every 2s ---
  const interval = setInterval(load, 2000);
  onMount(() => {
    load();
    return () => clearInterval(interval);
  });
</script>

<h1>Node Apps</h1>

{#each Object.entries(apps) as [name, app]}
  <div class="node-box">
    <b>{name}</b> — {app.status} (v{app.version || 'unknown'})
    {#if app.error}
      <div class="error">Error: {app.error}
        <button on:click={() => acknowledgeError(name)}>Acknowledge</button>
      </div>
    {/if}

    <div class="controls">
      {#if app.status === 'stopped' && !app.error}
        <button on:click={() => start(name)}>Start</button>
      {:else if app.status === 'running'}
        <button on:click={() => shutdown(name)}>Shutdown</button>
        <button on:click={() => restart(name)}>Restart</button>
        <button on:click={() => update(name)}>Update</button>
      {/if}
    </div>

    <label class="keep-alive">
      <input type="checkbox" bind:checked={app.keep_alive} on:change={async () => {
        await toggleKeepAlive(name, app.keep_alive);
      }}>
      Keep Alive
    </label>
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

.keep-alive {
  display: block;
  margin-top: 5px;
  font-size: 0.9em;
}
</style>