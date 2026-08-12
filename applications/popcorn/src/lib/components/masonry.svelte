<script>
  import { onMount, tick } from 'svelte';

  export let column = 300; // px
  export let row = 10;     // px

  let container;
  let check; // <link> pealt saadud ühe column width

   // Funktsioon, mis mõõdab sloti child elemente ja arvutab neile grid-row-end
  async function measureChildren() {
    if (!container || !check) return;

    const colWidth = check.offsetWidth;
    const children = Array.from(container.children).filter(c => c.tagName !== 'LINK');

    // Maksimaalne span-i arv containeri laiuse põhjal
    const maxCols = Math.floor(container.clientWidth / column);

    await tick();
    
    // peidame ja paneme absolute + column width
    children.forEach(child => {
      const requestedCols = parseInt(child.getAttribute('column') || '1', 10);

      // arvutame dünaamilise span-i
      const span = Math.min(requestedCols, maxCols);   // container = span count
      const finalSpan = Math.max(1, span);             // min span 1

      child.dataset.currentSpan = finalSpan; // testimiseks
      child.style.position = 'absolute';
      child.style.visibility = 'hidden';
     // child.style.overflow = 'hidden';
      child.style.width = `${colWidth * finalSpan}px`; // korrutame span-ga
      child.style.marginBottom = `${row}px`;
      child.style.gridColumn = `span ${finalSpan}`; // lisame ka grid-column
    });

    await tick(); // ootab, et browser rakendaks stiilid

    // mõõdame ja lisame testimiseks height ning grid-row-end
    setTimeout( () =>
      children.forEach(child => {
        const height = child.offsetHeight;
        child.dataset.h = height; // testimiseks

        // arvutame rows, arvestades margin-bottom
        const rows = Math.max(1, Math.round(height / row)) + 2; /* gap */
        child.style.gridRowEnd = `span ${rows}`;

        // eemaldame mõõtmiseks vajalikud stiilid
        child.style.position = '';
        child.style.visibility = '';
        child.style.width = '';
      }), 50)
  }

  onMount(() => {
    measureChildren();
    window.addEventListener('resize', measureChildren);
  });
</script>

<section
  class="masonry"
  bind:this={container}
  style="--min:{column}px; --gap:{row}px; --row:{row}px"
>
  <slot />
  {#each Array(Math.floor(container?.clientWidth / column) || 1) as _}
    <link bind:this={check} class="flex"/>
  {/each}
</section>

<style>
  .masonry {
    display: grid;
    grid-auto-rows: var(--row);
    grid-auto-flow: dense;
    column-gap: var(--gap);
    width: 100%;
    grid-template-columns: repeat(auto-fit, minmax(var(--min), 1fr));
  }
</style>



<!--
  import Masonry from '$lib/global/masonry.svelte'

  <Masonry column={250} row={10}>
    <div style="display: grid" column="1">
      abc
    </div>

    <div style="display: grid">
      123
    </div> 
  </Masonry>
-->


<!-- TÖÖTAB -->