<script>
  // discovery -> poster.svelte
  export let src, alt;

  let imgEl,
      isLoaded = false,
      loadError = false;

  function onLoad() {
    isLoaded = true;
    loadError = false;
  }

  function onError() {
    isLoaded = false;
    loadError = true;
  }
</script>

{#if !isLoaded && !loadError}
  <div class="skeleton"></div>
{/if}

<img bind:this={imgEl} src={src} alt={alt} on:load={onLoad} on:error={onError} class:hide={!isLoaded}
/>

<style>
  .skeleton {
    display: block;
    width: -webkit-fill-available;
    height: -webkit-fill-available;
    min-height: 150px;
    background: linear-gradient(90deg, #eee, #3f3f3f, #eee);
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
    border-radius: 5px;
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  
    img {
    position: relative;
    animation: loadAnimation 1s forwards; }

  @keyframes loadAnimation {
    from { opacity: 0; }
    to { opacity: 1; }
  }
</style>