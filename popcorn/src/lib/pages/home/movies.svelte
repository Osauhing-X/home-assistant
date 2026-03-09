<script>
  import Card from '$lib/pages/movie/components/poster.svelte'

  import { base } from '$app/paths';
  import { onMount } from "svelte";
  import { resolve } from '$app/paths';

  $: list = []

  onMount(async () => {
    const res = await fetch(base + `/@_movie/json`)

    if(res.ok) {
      let data = await res.json()
          list = data?.data?.slice(0, 20) }
  })

</script>


<center class="grid gap _2">
  <header class="flex _wrap gap _space">
    <h2>Current Popular</h2>
    <input type="button" value="View all" on:click={ ()=> window.location.href = resolve('/s_all')}>
  </header>
  <section id="movies">
    <div class="flex gap _3">
      {#each list as object (object)}
        <Card {object}/>
      {/each}
    </div>
  </section>
  <div class="controls">
  	<button on:click={() => list = [list.at(-1), ...list.slice(0,-1)]}>Prev</button>
  	<button on:click={() => list = [...list.slice(1), list[0]]}>Next</button>
  </div>
</center>




<style>
  #movies {
    padding: 2px 0;
    overflow: hidden;}
  #movies :global(a){
    min-width: 135px; }

  header a {
    user-select: none;
    align-content: center;
    background: #ddd;
    text-decoration: none;
    padding: 0 10px;
    box-shadow: 0 0 0 1px #000;
    color: #000;
    border-radius: 2px; }
  header a:hover {
    background: #ccc; }
  header a:active {
    filter: blur(1px); }
</style>