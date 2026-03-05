<script>
  export let data = null;

  import Masonry from "$lib/components/masonry.svelte";
</script>


 <Masonry column={300} row={10}>
  {#each data as season}
    <div class="flex wrap gap black" style="column-gap: 10px;">
      <img src={season.poster_path ? `https://image.tmdb.org/t/p/w500${season.poster_path}` : ""} aria-label="poster" alt="poster" >
      <div>
        <h3>{season.name}</h3>
        {#if !season?.overview}<br>{/if}
          <svelte:element this={season?.overview ? "flex" : "grid"} style="gap: 5px">
            {#if season?.air_date}<span>{season.air_date}</span>{/if}
            {#if season?.episode_count}<span>Episode count: {season.episode_count}</span>{/if}
          </svelte:element>
        {#if season?.overview}<small>{season.overview}</small>{/if}
      </div>
    </div>
  {/each}
</Masonry>


<style>
  .black {
    padding: 10px;
    border-radius: 3px;
    background: var(--base);
    background-image: url('/website/noise.png') !important;
    background-attachment: fixed;}

  img {
    --height: 100px;
    position: sticky;
    top: 1em;
  }
</style>