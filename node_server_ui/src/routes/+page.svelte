<script>
  let apps = [];

  async function load() {
    const res = await fetch('/');
    apps = await res.json();
  }

  async function restart(name) {
    await fetch(`/?name=${name}&action=restart`, { method: 'POST' });
    load();
  }

  async function pull(name) {
    await fetch(`/?name=${name}&action=pull`, { method: 'POST' });
  }

  load();
</script>

<h1>Node Apps</h1>

{#each Object.entries(apps) as [name, app]}
  <div>
    <b>{name}</b> — {app.status}
    <button on:click={() => restart(name)}>Restart</button>
    <button on:click={() => pull(name)}>Pull & Install</button>
  </div>
{/each}