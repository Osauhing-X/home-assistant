<script>
  export let open = true
  export let elem = 'div'

 /* <Card elem="section">
    	<div slot="summary" on:click={()=> open = !open}>Blog Post Title</div>
    	...
    </Card> */
</script>


<svelte:element this={elem} class="grid gap">
  <slot name="header" />

  {#if open} <slot /> {/if}
</svelte:element>