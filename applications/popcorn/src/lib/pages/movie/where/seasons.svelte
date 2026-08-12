<script>
  export let data = null;

  import Masonry from "$lib/components/masonry.svelte";
  import Image from "$lib/components/image.svelte";
</script>


<section class="grid gap _5">
  {#each data as season}
    <div class="grid" id="seasons" title={season?.overview} >
      <div>
      <Image src={season.poster_path ? `https://image.tmdb.org/t/p/w500${season.poster_path}` : ""} alt="poster" />
      </div>
      <div class="grid gap">
        <h3>{season.name}</h3>
        {#if season?.air_date}
          <span>{season.air_date}</span>{/if}
        {#if season?.episode_count}
          <span>Episode count: {season.episode_count}</span>{/if}
      </div>
    </div>
  {/each}
</section>


<style lang="scss">
  #seasons {
    column-gap: 10px;
    grid-template-columns: 100px 1fr;}

  h3 {margin: 0;}

  span {
    background: #000;
    color: #fff;
    color-scheme: light;
    border-radius: 3px;
    padding: 2px 10px;
    width: max-content;
  }

  section {
    position: relative;
    gap: 10px;
    grid: min-content/repeat(auto-fill,minmax(250px,1fr));
    grid-auto-flow: row dense;
    justify-items: start;

    @media (max-width:600px) { --em: 5em }
  }
</style>