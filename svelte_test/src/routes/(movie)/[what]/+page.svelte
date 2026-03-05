<script>
  import { view, fav } from '$lib/movie/scripts/favorite'
  import { page } from '$app/stores';
  import { resolve } from '$app/paths';

// --- --- ---

  import Card from "$lib/movie/components/poster.svelte"

  onMount(()=> fav().get())

  $: filtered = {}

  if($view) filtered = Object.fromEntries( Object.entries($view).filter(([key]) => ['movie', 'tv', 'person'].includes(key)) )

// --- # Language
  import { get_i18n } from '$lib/assets/language.js';
  let i18n = get_i18n($page.data.meta, '/discover/favorite')

// --- # Content - 
  async function get_favorite(what, id) {
    const res = await fetch($page.data.base + '@_movie/solo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ what, id })
    })

    if(res.ok) return await res.json()
  }


// --- # Inports
  import Info from '$lib/components/info.svelte';
  import Back from "$lib/movie/image/back.svg?raw"
    import { onMount } from 'svelte';
</script>





<center class="padding top bottom grid gap _5">
  <section>
    <a class="null flex" href={resolve('/')}>
        {@html Back} {$i18n?.back}
      </a>
  </section>


  {#await Object.fromEntries( Object.entries($view ?? {}).filter(([key]) => ['movie', 'tv', 'person'].includes(key)) ) then filtered}
    {#each Object.keys(filtered) as what}
      <section title={what}>
        <h2 class="null">{$i18n[what]}</h2>
        <div class="grid trending">
        {#each filtered[what] as where}
          {#if typeof where === "number"}
            {#await get_favorite(what, where) then object}
              <Card {object} show={false} />
            {/await}
          {/if}
        {/each}
        </div>
      </section>
    {/each}

    {#if !Object.values(filtered).flat().length}
      

      <section>
        <Info text={$i18n?.empty} btn={false} type="🔴"/>
      </section>
    {/if}
  {/await}
</center>

<style lang="scss">
  a {
    width: min-content;
    font-family: 'extaas';
    color: var(--reverse) !important;
    text-decoration: none;
    align-items: center;
    gap: 10px;
    padding-right: 15px !important;
  
    &.null {
      background: var(--transparent);
      border: 0;
      padding: 5px 15px 5px 10px;
      line-height: 10px;
      max-height: 44px;

      &:hover {
        outline: 1px solid var(--primary);
      }
    }
  }


  .trending {
    position: relative;
    gap: 10px;
    grid: min-content/repeat(auto-fill,minmax(var(--em, 7em),1fr));
    grid-auto-flow: row dense;
    justify-items: start;

    @media (max-width:600px) { --em: 5em }
  }

</style>