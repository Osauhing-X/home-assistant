<script>
  import { onMount, onDestroy } from 'svelte';
  import { base } from '$app/paths';
  import { browser } from '$app/environment';

  let apps = {};
  let logs = {}; // logid per node
  let pending = {};
  let actionError = {};

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
      const res = await fetch(`${base}/@_logs?name=${name}&lines=200`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok) return logs[name] = ['Failed to load logs'];
      logs[name] = data.lines;
    } catch(e) {
      logs[name] = [`Failed to load logs: ${e.message}`];
    }
  }

  // --- Auto refresh ---
  let interval;

  onMount(() => {
    load();
    interval = setInterval(() => {
      load();
      for (const name of Object.keys(apps)) get_logs(name);
    }, 2000);
    return () => clearInterval(interval);
  });

  onDestroy(() => clearInterval(interval));

  // --- control functions ---
  async function runAction(name, action) {
    pending = { ...pending, [name]: action };
    actionError = { ...actionError, [name]: '' };
    try {
      const res = await fetch(`${base}/@_${action}?name=${encodeURIComponent(name)}`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok || data.error) throw new Error(data.error || `Request failed (${res.status})`);
      await load();
    } catch (e) {
      actionError = { ...actionError, [name]: e.message };
    } finally {
      pending = { ...pending, [name]: '' };
    }
  }

  const start = (name) => runAction(name, 'start');
  const shutdown = (name) => runAction(name, 'stop');
  const restart = (name) => runAction(name, 'restart');
  const update = (name) => runAction(name, 'update');
  async function acknowledgeError(name) { await fetch(base + `/@_error?name=${name}`, { method:'POST' }); load(); }
  async function toggleKeepAlive(name, value) { await fetch(base + `/@_pm2?name=${name}&keep_alive=${value}`, { method:'POST' }); load(); }
</script>


<main>
  <section>
    <h1>Node application</h1>
  </section>

<section class="grid">
  {#each Object.entries(apps) as [name, app]}
    <details>
      <summary>
        <b>{name}</b>
        <div>
          {#if app.error}<span class="error_span">Error</span>{/if}
          <span class={app.status}>{app.status}</span>
          <span>v{app.version || 'unknown'}</span>
        </div>
      </summary>
      <section>
        <nav>
          {#if app.status === 'stopped' && !app.error}
            <button disabled={!!pending[name]} on:click={() => start(name)}>Start</button>
          {:else if app.status === 'running'}
            <button disabled={!!pending[name]} on:click={() => shutdown(name)}>Shutdown</button>
            <button disabled={!!pending[name]} on:click={() => restart(name)}>Restart</button>
          {/if}
          <button disabled={!!pending[name]} on:click={() => update(name)}>Github Pull</button>
          <label class="keep-alive">Keep Alive<input type="checkbox" bind:checked={app.keep_alive} on:change={async () => {await toggleKeepAlive(name, app.keep_alive); }}> 
        </label>
      </nav>

        {#if pending[name]}<div class="action-status">{pending[name]} in progress…</div>{/if}
        {#if actionError[name]}<div class="action-error">{actionError[name]}</div>{/if}

    

        {#if app.error}
          <hr style="border-color: #222;">
          <div class="error_logs">Error: {app.error}</div>
          <button on:click={() => acknowledgeError(name)}>Acknowledge</button>
        {/if}

        <hr style="border-color: #222;">

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

  {#if !Object.entries(apps).length}
    <hr style="margin: 2em 0;">
    <b style="color: palevioletred;">No nodes added</b>
  {/if}
</section>
</main>

<style>
  main {
    max-width: 900px;
    margin: 0 auto;
    padding: 1em; }

  .grid {
    display: grid; gap: 1em;
    grid-auto-rows: min-content; }

  details {
    color: #ddd;
    border-radius: 2px;
    outline: 1px solid #222;}

  summary {
    cursor: pointer;
    background: #1c1c1c;
    display:flex;
    justify-content: space-between;
    flex-wrap: wrap; gap: 5px;
    padding: 10px;}
    summary > div {
      display: flex;
      gap: 5px}


  details section { 
    background: #111;
    padding: 10px; }
    .keep-alive {
      float: inline-end;
      display: inline-flex; gap: 5px;
      align-items: flex-end; }


span {
  user-select: none;
  border-radius: 3px;
  background: #000;
  color: var(--override, #fff);
  padding: 3px 10px;
  font-family: monospace;
  text-transform: uppercase;}
.running { --override: #0f0; font-weight: bold; }
.stopped, .error_span { --override: #f55; font-weight: bold; }


.error_logs {
  margin-bottom: 5px;
  background:#111;
  color:#faa;
  padding:5px;
  border-radius:3px;
  max-height:300px;
  overflow:auto;
  font-family:monospace;
  font-size:0.8em; }

.action-status, .action-error {
  margin-top: 8px;
  font: 0.75em monospace;
  color: #aaa; }
.action-error { color: #f88; }
button:disabled { cursor: wait; opacity: 0.55; }

.logs { background:#111; color:#0f0; padding:5px; max-height:300px; overflow:auto; font-family:monospace; font-size:0.8em; }
</style>
