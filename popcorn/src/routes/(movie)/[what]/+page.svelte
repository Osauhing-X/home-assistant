<script>
  import { view, fav } from '$lib/pages/movie/scripts/favorite'
  import { page } from '$app/stores';
  import { resolve } from '$app/paths';

// --- --- ---

  import Card from "$lib/pages/movie/components/poster.svelte"

  onMount(()=> fav().get())

  $: filtered = {}

  if($view) filtered = Object.fromEntries( Object.entries($view).filter(([key]) => ['movie', 'tv', 'person'].includes(key)) )


// --- # Content - 
  async function get_favorite(what, id) {
    const res = await fetch($page.data.base + '/@_movie/solo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ what, id })
    })

    if(res.ok) return await res.json()
  }


// --- # Inports
  import Info from '$lib/components/info.svelte';
    import { onMount } from 'svelte';


  // Language
  import language_pack from '$lib/pages/movie/i18n.yaml'
  import { request } from '$lib/assets/request'
  let i18n = request('what_favorite', language_pack)

  import Header from '$lib/components/header.svelte';
  import Grid from '$lib/components/grid.svelte'


  import { navigating } from '$app/stores';
</script>



<Header />

{#if !$navigating}
  <section class="grid gap _5 around" style="">
    {#await Object.fromEntries( Object.entries($view ?? {}).filter(([key]) => ['movie', 'tv', 'person'].includes(key)) ) then filtered}
      {#each Object.keys(filtered) as what}
        <section title={what}>
          <h2 class="null">{$i18n[what]}</h2>
          <Grid padding="5px 0">
            {#each filtered[what] as where}
              {#await get_favorite(what, where) then object}
                <Card {object} show={false} />
              {/await}
            {/each}
          </Grid>
        </section>
      {/each}
      
      {#if !Object.values(filtered).flat().length}
        <section>
          <Info text={$i18n?.empty} btn={false} type="🔴"/>
        </section>
      {/if}
    {/await}
  </section>
{/if}

<style lang="scss">
  .around {
    margin: 1em auto; padding: 1em;
  }


</style>