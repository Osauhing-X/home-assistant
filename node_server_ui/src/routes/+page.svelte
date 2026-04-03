<script>
  import { resolve } from '$app/paths';

  let apps = [];

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



  async function test(){
    console.log(await fetch(`http://localhost:2999/`))
  }
</script>

<h1>Node Apps</h1>

{#each Object.entries(apps) as [name, app]}
  <div>
    <b>{name}</b> — {app.status}
    <button on:click={() => restart(name)}>Restart</button>
    <button on:click={() => pull(name)}>Pull & Install</button>
  </div>
{/each}

<button on:click={()=>test()}>Log</button>