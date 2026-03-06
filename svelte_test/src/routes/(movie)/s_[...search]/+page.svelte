<script>
  import { page, navigating } from '$app/stores'

  import Card from '$lib/pages/movie/components/poster.svelte'
  
  export let data

  import { fav } from '$lib/pages/movie/scripts/favorite.js'
  fav().get()

// Language
  import language_pack from '$lib/pages/movie/i18n.yaml'
  import { request } from '$lib/assets/request'

// Imports
  import Header from '$lib/components/header.svelte';
  import Search from '$lib/pages/movie/what/search.svelte';
  import SelectPage from '$lib/pages/movie/what/select_page.svelte';
</script>
<Header>
  <Search i18n={request('what_search', language_pack)} />
</Header>

{#if data?.data && !$navigating}
  <section class="grid trending" data-sveltekit-preload-data="tap">
    {#each data.data || [] as object, nr}
      <Card {object} />
    {/each}
  </section>
  <SelectPage json={data.pages}/>
{/if}


<style lang="scss">
  section {
    margin: 1em auto;
    padding: 1em;
    position: relative;
    gap: 10px;
    grid: min-content / repeat(auto-fill,minmax(var(--em, 7em),1fr));
    grid-auto-flow: row dense;
    justify-items: start;
    @media (max-width:600px) { --em: 5em }
  }

</style>