<script>
  import { onMount } from 'svelte';

  let apps = {};

  // --- LOAD ---
  async function load() {
    try {
      const res = await fetch('/@_get');
      apps = await res.json();
    } catch (e) {
      console.error('Load failed:', e);
    }
  }

  // --- ACTIONS ---
  async function start(name) {
    await fetch(`/@_start?name=${name}`, { method: 'POST' });
    load();
  }

  async function shutdown(name) {
    await fetch(`/@_shutdown?name=${name}`, { method: 'POST' });
    load();
  }

  async function restart(name) {
    await fetch(`/@_restart?name=${name}`, { method: 'POST' });
    load();
  }

  async function update(name) {
    await fetch(`/@_update?name=${name}`, { method: 'POST' });
  }

  async function toggleBoot(name, value) {
    await fetch(`/@_boot?name=${name}&value=${value}`, { method: 'POST' });
    load();
  }

  // --- INIT ---
  onMount(() => {
    load();
    const i = setInterval(load, 3000);
    return () => clearInterval(i);
  });
</script>

<h1>Node Apps</h1>

{#each Object.entries(apps) as [name, app]}
  <div class="card">
    <div class="row">
      <b>{name}</b>
      <span class={`status ${app.status}`}>{app.status}</span>
    </div>

    <div class="buttons">
      {#if app.enabled}
        <button on:click={() => shutdown(name)}>Stop</button>
        <button on:click={() => restart(name)}>Restart</button>
        <button on:click={() => update(name)}>Update</button>
      {:else}
        <button on:click={() => start(name)}>Start</button>
      {/if}
    </div>

    <label class="boot">
      <input
        type="checkbox"
        checked={app.boot_on_start}
        on:change={(e) => toggleBoot(name, e.target.checked)}
      />
      Boot on start
    </label>
  </div>
{/each}

<style>
  .card {
    background: #111;
    color: #ccc;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 6px;
  }

  .row {
    display: flex;
    justify-content: space-between;
  }

  .status.running { color: #4caf50; }
  .status.stopped { color: #f44336; }
  .status.restarting,
  .status.starting { color: #ff9800; }

  .buttons button {
    margin-right: 5px;
    margin-top: 5px;
  }

  .boot {
    display: block;
    margin-top: 5px;
    font-size: 0.9em;
  }
</style>