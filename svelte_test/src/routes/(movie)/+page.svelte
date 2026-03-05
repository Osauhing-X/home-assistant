<script>
  import { onMount } from 'svelte'
  import { page, navigating } from '$app/stores'
  import { browser } from '$app/environment'

  let data = {}

  async function get_data() {
    const res = await fetch(`/@_movie/get_all` + $page.url.search)
    data = await res.json()
  }

  // ainult browseris
  onMount(() => {
    get_data()
  })

  // reageeri URL muutusele ainult browseris
  $: if (browser) {
    $page.url
    get_data()
  }

  $: is_start = $page.url.href.endsWith($page.url.pathname)

  $: top_content =
    is_start
      ? true
      : $page.url.searchParams.get('page') == 1

  import { view } from '$lib/movie/discover_store.js'

  $: favorite =
    !!Object
      .values(
        Object.fromEntries(
          Object.entries($view ?? {})
          .filter(([key]) =>
            ['movie','tv','person'].includes(key)
          )
        )
      )
      .flat()
      .length

  import { i18n, get_i18n } from '$lib/assets/language.js'

  import Fav from "$lib/movie/index/favorite.svelte"
  import Search from "$lib/movie/index/search.svelte"
  import Card from "$lib/movie/poster.svelte"
  import Number from "$lib/movie/index/select_page.svelte"
  import Top from "$lib/movie/index/top_content.svelte"
</script>

<center class="padding top bottom grid gap _5">
  {#if !$navigating}

    {#if is_start}
      <section class="grid">
        {@html $i18n?.intro}
        <Fav {i18n} />
      </section>
      <!--<Top json={$page?.data?.data[0]} />-->
    {/if}
  
  <section class="grid">

    <div class="flex gap wrap" style="z-index: 50;">
      {#if favorite}
        <a href="discover/favorite" class="fav">⭐</a>
      {/if}
      <Search i18n={get_i18n($page.data.meta, 'search')} />

      <Number json={data?.pages} />
    </div>
    
    {#if data?.data && !$navigating}
      <div class="grid trending" data-sveltekit-preload-data="hover">
        {#each data.data || [] as object, nr}
          {#if top_content && nr == 0}
            {null}
          {:else}
            <Card {object} />
          {/if}
        {/each}
      </div>
    {:else}
      {#await new Promise(r => setTimeout(() => r(), 2000))}
        <br aria-label="loading">
      {:then}
        {$i18n?.no_data}
      {/await}
    {/if}

    {#if data?.data}
      <Number json={data?.pages} />
    {/if}
  </section>
  {/if}
</center>


<style lang="scss">
  .fav {
    transition: .5s;
    position: relative;
    padding: 0.38em;
    border: 1px solid var(--transparent);
    text-decoration: none;

    &:hover {
      background: var(--transparent);
      border: 1px solid #aaa; } }

  section.grid {
    row-gap: 2em;

    .trending {
      position: relative;
      gap: 10px;
      grid: min-content / repeat(auto-fill,minmax(var(--em, 7em),1fr));
      grid-auto-flow: row dense;
      justify-items: start;
      @media (max-width:600px) { --em: 5em }
    }
  }
  
</style>