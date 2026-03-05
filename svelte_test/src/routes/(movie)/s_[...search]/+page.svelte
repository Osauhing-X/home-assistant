<script>
  import { page, navigating } from '$app/stores'

  import Card from '$lib/movie/components/poster.svelte'
  
  export let data
</script>


{#if data?.data && !$navigating}
  <div class="grid trending" data-sveltekit-preload-data="tap">
    {#each data.data || [] as object, nr}
      <Card {object} />
    {/each}
  </div>
{/if}


<style lang="scss">
  .trending {
    position: relative;
    gap: 10px;
    grid: min-content / repeat(auto-fill,minmax(var(--em, 7em),1fr));
    grid-auto-flow: row dense;
    justify-items: start;
    @media (max-width:600px) { --em: 5em }
  }

</style>