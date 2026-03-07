<script>
  import { resolve } from '$app/paths';
  import Calender from '$lib/pages/calender/module.svelte';
  import { selected } from "$lib/pages/calender/calender_store";
</script>


<a href={resolve('/s_all')}>Movies</a>


<Calender />

{#if $selected.length}
  <center style="margin: 2em auto;">
    {#each $selected as {title, url, img}}
      {#if url && img}
        <a href={url} style="display: block; width: 180px;">
          <img src={img} alt={title} width="100">
        </a>
      {/if}
    {/each}
  </center>
{/if}
