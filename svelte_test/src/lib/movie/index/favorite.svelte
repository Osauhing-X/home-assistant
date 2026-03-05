<script>
  import { onMount } from 'svelte';
  import { view } from '$lib/movie/discover_store.js'

  export let i18n = null

  $: list = {}

  onMount(() => {
    list = $view
    if(list?.link) delete list.link })
</script>

{#if list && Object.keys(list) != ""}
  <section class="flex">
    <b>{@html $i18n?.favorite}</b>
    {#each Object.keys(list) || [] as what, nr}
      <a href={what} count={$view[what].length}>{what}</a>
    {/each}
  </section>
{/if}

<style lang="scss">
  section {
    gap:7px;
    width: fit-content;
  }
  a {
    background: var(--main);
  
    position: relative;
    display: flex;
    align-content: center;
    justify-content: center;
    font-size: large;
    text-decoration: none;
    padding-left: 10px;
    outline: 1px solid #2222;


    &[count]::after {
      content: attr(count);
      font-size: 15px;
      background: var(--transparent);
      border: 3px solid var(--main);
      margin-left: 5px;
      padding: 0 5px;
      
    }


  }
</style>
