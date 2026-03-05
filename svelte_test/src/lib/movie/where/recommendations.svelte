<script>
  export let data = null

  import Card from "../poster.svelte"
</script>

<div class="grid list">
  {#each data as object}
    <Card {object} />
  {/each}
</div>


<style>
  .list {
    position: relative;
    gap: 10px;
    grid: min-content/repeat(auto-fill,minmax(var(--em, 7em),1fr));
    grid-auto-flow: row dense;
    justify-items: start; }

  @media screen and (max-width:600px) {
    .list { --em: 5em} }
</style>