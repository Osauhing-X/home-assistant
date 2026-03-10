<script>
  import { page, navigating } from '$app/stores';
  import { resolve } from '$app/paths';

  export let json;

  let numbers, current, min, max, last_page
  
  function range() {
    let arr = [];
    for (let i = min; i <= max; i++) arr.push(i);
    numbers = arr;
  }

  function go(nr){
    const url = new URL(  resolve("/s_all" + json.url), $page.url);
    url.searchParams.set('page', nr);
    return resolve("/s_all" + json.url);
  }

  $: {
    if($page.url.search || !$navigating){
      current = json?.current ?? {}

      // NEW
      min = min = Math.max(current - 2, 1) // korras
      
      let api_limit = Math.floor(500 / json?.fetch) // korras // api limit

      last_page = Math.min(Math.round(json?.total / json?.fetch), api_limit) // korras // content limit

      max = Math.min(current + 2, last_page)

      if(min && max) range()
    }
  }
</script>


{#if json && !$navigating}
  <nav class="flex" style="gap:5px" data-sveltekit-preload-data="hover">
    <a href={go(1)} class:disbled={current <= 1}>◁◁</a>
      {#each numbers as nr}
        <a href={nr == current ? null : go(nr)} class:active={nr == current}>{nr}</a>
      {/each}
      <a href={go(last_page)} class:disbled={current >= last_page}>▷▷</a>
  </nav>
{/if}

<style>
  nav {
    place-self: center;
    width: max-content;
    margin-bottom: 2em;
  }


  a {
    text-decoration: none;
    border: 1px solid var(--transparent);
    transition: .5s;

    padding: 0.5em 0.7em;
    width: fit-content;
  }

  .active {
    color: var(--primary);
    border: 1px solid var(--primary);
    background: var(--transparent);
  }
  .disbled {
    pointer-events: none;
    filter: blur(3px);
  }

  a:hover {
    border: 1px solid #aaa;
    color: #aaa
  }
</style>