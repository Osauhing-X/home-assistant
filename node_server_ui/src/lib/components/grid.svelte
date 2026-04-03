<script>
  export let column = 150;
  export let padding = "1em";
  let container, clientWidth = 0
</script>


<section class="grid" style="--c:{column}px; --w:{clientWidth}px" bind:this={container} data-sveltekit-preload-data="tap">
  <div class="observe"> <link bind:clientWidth class="flex"/> </div>
  <div class="content" style="--p: {padding}"> <slot /> </div>
</section>


<style>
  link { width: 100%; }

  .observe, .content {
    display: grid;
    width: -webkit-fill-available;
    padding: var(--p);
    position: relative;
    gap: 10px;
    grid: min-content / repeat(auto-fill,minmax(var(--c),1fr));
    grid-auto-flow: row dense;
    justify-items: start; }

  .observe { --p: 0 1em; }
</style>