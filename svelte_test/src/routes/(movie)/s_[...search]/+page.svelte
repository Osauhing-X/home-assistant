<script>
  import { page, navigating } from '$app/stores'

  import Card from '$lib/movie/components/poster.svelte'
  
  export let data

  import { fav } from '$lib/movie/scripts/favorite.js'
  fav().get()

// Language
  import language_pack from '$lib/movie/i18n.yaml'
  import { request } from '$lib/assets/request'

// Imports
  import Header from '$lib/movie/what/header.svelte';
  import Search from '$lib/movie/what/search.svelte';
  import SelectPage from '$lib/movie/what/select_page.svelte';
</script>
<Header i18n={request('_header', language_pack)}>
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
    margin: 3em auto;
    padding: 1em;
    position: relative;
    gap: 10px;
    grid: min-content / repeat(auto-fill,minmax(var(--em, 7em),1fr));
    grid-auto-flow: row dense;
    justify-items: start;
    @media (max-width:600px) { --em: 5em }
  }

</style>