<script>
  export let tag = "div";
  export let id = null;
  export let href = null;
  export let css = null; // class


  let inView = false;
  let observerElement;

  function observe(node) {
    const observer = new IntersectionObserver(([entry]) => {
      inView = entry.isIntersecting;
    }, {
      rootMargin: '1000px 0px',
      threshold: 0.01
    });

    observer.observe(node);

    return {
      destroy() {
        observer.disconnect();
      }
    };
  }
</script>


<svelte:element class:base={true} this={tag} {id} {href} class={css} use:observe bind:this={observerElement}>
  {#if inView}
    <slot />
  {:else}
    <link class="ghost">
  {/if}
</svelte:element>


<style>
  .base { position: relative; }

  .ghost {
    display: block;
    height: 100%;
    aspect-ratio: 2/3;
    width: var(--w);
  }
</style>