<script>
  import { resolve } from '$app/paths';

  let apps = [];
  export let data

  async function load() {
    const res = await fetch(resolve('/'));
    apps = await res.json();
  }

  async function restart(name) {
    await fetch(resolve(`/?name=${name}&action=restart`), { method: 'POST' });
    load();
  }

  async function pull(name) {
    await fetch(resolve(`/?name=${name}&action=pull`), { method: 'POST' });
  }

  load();




  import { onMount } from 'svelte';
  onMount(async () => {
    console.log(await fetch(`http://localhost:2999/`))

    let url_1 = resolve('/')
    console.log(url_1)
    console.log(await fetch(url_1))

    let url_2 = data.base
    console.log(url_2)
    console.log(await fetch(url_2))


  })
</script>

<h1>Node Apps</h1>

{resolve('/')}

{#each Object.entries(apps) as [name, app]}
  <div>
    <b>{name}</b> — {app.status}
    <button on:click={() => restart(name)}>Restart</button>
    <button on:click={() => pull(name)}>Pull & Install</button>
  </div>
{/each}

