<script>
  import { onMount, onDestroy } from 'svelte';
  import { base } from '$app/paths';
  import { browser } from '$app/environment';

  let apps = {};
  let logs = {}; // logid per node

  async function load() {
    if (!browser) return;
    try {
      const res = await fetch(base + '/@_get');
      apps = await res.json();
    } catch(e) {
      console.error('Failed to load apps', e);
    }
  }

  async function get_logs(name) {
    try {
      const res = await fetch(base + `/@_logs?name=${name}&lines=50`);
      const data = await res.json();
      logs[name] = data.lines;
    } catch(e) {
      logs[name] = [`Failed to load logs: ${e.message}`];
    }
  }

  // --- Auto refresh ---
  const interval = setInterval(() => {
    load();
    for (const name of Object.keys(apps)) {
      get_logs(name);
    }
  }, 2000);

  onMount(() => {
    load();
    return () => clearInterval(interval);
  });

  onDestroy(() => clearInterval(interval));

  // --- control functions ---
  async function start(name) { await fetch(base + `/@_start?name=${name}`, { method:'POST' }); load(); }
  async function shutdown(name) { await fetch(base + `/@_stop?name=${name}`, { method:'POST' }); load(); }
  async function restart(name) { await fetch(base + `/@_restart?name=${name}`, { method:'POST' }); load(); }
  async function update(name) { await fetch(base + `/@_update?name=${name}`, { method:'POST' }); load(); }
  async function acknowledgeError(name) { await fetch(base + `/@_error?name=${name}`, { method:'POST' }); load(); }
  async function toggleKeepAlive(name, value) { await fetch(base + `/@_pm2?name=${name}&keep_alive=${value}`, { method:'POST' }); load(); }
</script>

<h1>Node Apps</h1>

{#each Object.entries(apps) as [name, app]}
<details>
  <summary>
    <b>{name}</b>
    <div>
      <span>v{app.version || 'unknown'}</span>
      <span class={app.status}>{app.status}</span>
      {#if app.error}<span class="error">Error</span>{/if}
    </div>
  </summary>
  <section>
    <nav>
      {#if app.status === 'stopped' && !app.error}
        <button on:click={() => start(name)}>Start</button>
      {:else if app.status === 'running'}
        <button on:click={() => shutdown(name)}>Shutdown</button>
        <button on:click={() => restart(name)}>Restart</button>
      {/if}
      <button on:click={() => update(name)}>Github Pull</button>
      <label class="keep-alive">
        <input type="checkbox" bind:checked={app.keep_alive} on:change={async () => {await toggleKeepAlive(name, app.keep_alive); }}> Keep Alive
      </label>
    </nav>

    <hr>

    {#if app.error}
      <div class="error">Error: {app.error}
        <button on:click={() => acknowledgeError(name)}>Acknowledge</button>
      </div>
    {/if}

    <hr>

    <div class="logs">
      <pre>
        {#if logs[name]}
          {logs[name].join('\n')}
        {:else}
          Loading logs...
        {/if}
      </pre>
    </div>
  </section>
</details>
{/each}

<style>
details { background: #eee; color: #222; padding: 10px; margin: 5px 10px; }
summary { display:flex; justify-content: space-between; flex-wrap: wrap; gap: 5px; }
section { background: #fff; border-radius: 5px; padding: 10px; }
.running { color: #0f0; font-weight: bold; }
.stopped { color: #f55; font-weight: bold; }
.error { color: #f88; margin-top:5px; font-size:0.9em; }
.error button { margin-left:10px; background:#f55; color:#fff; border:none; padding:2px 6px; border-radius:3px; cursor:pointer; }
.error button:hover { background:#faa; }
.keep-alive { display:block; margin-top:5px; font-size:0.9em; }
.logs { background:#111; color:#0f0; padding:5px; border-radius:3px; max-height:300px; overflow:auto; font-family:monospace; font-size:0.8em; }
</style>