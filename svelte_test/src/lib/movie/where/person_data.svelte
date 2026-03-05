<script>
  export let data;

  import { page, navigating } from '$app/stores';
  
  let show, country_code; // page_url = $page?.params?.where ? window.location.href : window.location.href+"/"+data.id;


  $: data, show = data?.providers?.languages.length > 0
  $: innerWidth = 0



    import { onMount } from 'svelte';

  import Card from '$lib/movie/components/poster.svelte';
</script>
<svelte:window bind:innerWidth />

  
<section id="data" class="grid" full="800">
  
  <header>
    <h1>{data.title ?? data.name}</h1>
    
    {#if data?.birthday}<span title="Tagline">{data.birthday}</span>{/if}
    {#if data?.known_for_department} <span> {data.known_for_department}</span> {/if}
  </header>

      <div class="flex gap" style="gap: 20px">
        <img style="--height:325px" src={data.profile_path ? `https://image.tmdb.org/t/p/w500${data.profile_path}` : ""} alt="poster">
        <p>{data.biography}</p>
      </div>
</section>

{#if data.movie.cast.length > 0}
  <section>
    <h2>Movie ({data.movie.cast.length})</h2>
    <div class="grid gap trending">
      {#each data.movie.cast || [] as object}
        <Card {object} />
      {/each}
    </div>
  </section>
{/if}

{#if data.tv.cast.length > 0}
  <section>
    <h2>Tv ({data.tv.cast.length})</h2>
    <div class="grid gap trending">
    {#each data?.tv?.cast || [] as object}
      <Card {object} />
    {/each}
    </div>
  </section>
{/if}
  









<style lang="scss">
  .gap { gap: 5px }



  #data.grid {
    gap:10px;
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