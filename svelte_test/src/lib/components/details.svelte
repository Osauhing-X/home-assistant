<script>
  export let open = true
  export let elem = 'div'

 /* <Card elem="section">
    	<div slot="summary">Blog Post Title</div>
    	...
    </Card> */
</script>


<svelte:element this={elem} class="grid gap">
  <button on:click={()=> open = !open} unset>
    <slot name="summary" />
  </button>

  {#if open} <slot /> {/if}
</svelte:element>