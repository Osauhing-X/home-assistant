<script>
  import { onMount } from 'svelte';

  let apps = {};

  async function load() {
    try {
      const res = await fetch('/api');
      apps = await res.json();
      console.log(apps);
    } catch (e) {
      console.error('Load failed:', e);
    }
  }

  async function restart(name) {
    await fetch(`/api?name=${name}&action=restart`, { method: 'POST' });
    load();
  }

  async function pull(name) {
    await fetch(`/api?name=${name}&action=pull`, { method: 'POST' });
  }

  onMount(load);
</script>


<h1>Node Apps</h1>


{#each Object.entries(apps) as [name, app]}
  <div>
    <b>{name}</b> — {app.status}
    <button on:click={() => restart(name)}>Restart</button>
    <button on:click={() => pull(name)}>Pull & Install</button>
  </div>
{/each}


<style>
  div {
    background: black;
    color: #aaa;
    padding: 5px;}
</style>