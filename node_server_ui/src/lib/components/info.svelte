<script>
  export let type = '⚡', text = 'null', show = true, btn = true;
</script>

{#if show}
  <info class="infokast" color={type} class:small={!btn}>
    <!-- Type -->
      {#if type == "⚪" ||  type == "⚡"}
        <svg class="center" id="info" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" stroke="none" stroke-width="0" stroke-linecap="round"  stroke-linejoin="round"><path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-.001 5.75c.69 0 1.251.56 1.251 1.25s-.561 1.25-1.251 1.25-1.249-.56-1.249-1.25.559-1.25 1.249-1.25zm2.001 12.25h-4v-1c.484-.179 1-.201 1-.735v-4.467c0-.534-.516-.618-1-.797v-1h3v6.265c0 .535.517.558 1 .735v.999z"/></svg>
      {:else if type == "🔴"}
        <svg class="center" id="danger" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" stroke="none" stroke-width="0" stroke-linecap="round" stroke-linejoin="round"><path d="M11.983,0a12.206,12.206,0,0,0-8.51,3.653A11.8,11.8,0,0,0,0,12.207,11.779,11.779,0,0,0,11.8,24h.214A12.111,12.111,0,0,0,24,11.791h0A11.766,11.766,0,0,0,11.983,0ZM10.5,16.542a1.476,1.476,0,0,1,1.449-1.53h.027a1.527,1.527,0,0,1,1.523,1.47,1.475,1.475,0,0,1-1.449,1.53h-.027A1.529,1.529,0,0,1,10.5,16.542ZM11,12.5v-6a1,1,0,0,1,2,0v6a1,1,0,1,1-2,0Z" /></svg>
      {:else if type == "🟡"}
        <svg class="center" id="warning" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" stroke="none" stroke-width="0" stroke-linecap="round" stroke-linejoin="round"><path d="M23.119,20,13.772,2.15h0a2,2,0,0,0-3.543,0L.881,20a2,2,0,0,0,1.772,2.928H21.347A2,2,0,0,0,23.119,20ZM11,8.423a1,1,0,0,1,2,0v6a1,1,0,1,1-2,0Zm1.05,11.51h-.028a1.528,1.528,0,0,1-1.522-1.47,1.476,1.476,0,0,1,1.448-1.53h.028A1.527,1.527,0,0,1,13.5,18.4,1.475,1.475,0,0,1,12.05,19.933Z" /></svg>
      {:else if type == "🟢"}
        <svg class="center" id="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" stroke="none" stroke-width="0" stroke-linecap="round" stroke-linejoin="round"><path d="M12,0A12,12,0,1,0,24,12,12.014,12.014,0,0,0,12,0Zm6.927,8.2-6.845,9.289a1.011,1.011,0,0,1-1.43.188L5.764,13.769a1,1,0,1,1,1.25-1.562l4.076,3.261,6.227-8.451A1,1,0,1,1,18.927,8.2Z" /></svg>
      {/if}


    <!-- Info -->
      <div>{@html text}</div>


    <!-- Close -->
      {#if btn}
        <input type="button" value="✖" on:click={()=> show = !show}>
      {/if}
  </info>
{/if}




<style>

  .infokast {
    --svg-size: 24px;

    width: fit-content;
    display: flex;
    gap: 10px;
    padding: 10px;
    background: var(--b);
    border: 2px solid var(--c);
    color: var(--c);
    border-radius: 5px;
    z-index: 50;
    --override: var(--svg-color);}

  .infokast[color="⚡"]{ --b:var(--transparent);  --c:var(--black); --svg-color: var(--primary)  }
  .infokast[color="🟢"]{ --b:#00ff2214;  --c:#15803d; --svg-color: #bbf7d0 }
  .infokast[color="🟡"]{ --b:#fbff0014;  --c:#cfc100; --svg-color: #f1f7bb }
  .infokast[color="🔴"]{ --b:#ff000014;  --c:#ff0000; --svg-color: #f7bbbb }
  .infokast[color="⚪"]{ --b:#00ffdd14;  --c:#157480; --svg-color: #bbeef7 }

  @media (max-width: 800px){
    .infokast.small { padding: 9px 15px 9px 15px; }
    svg { display: none; } }
  @media (min-width: 801px){
    .infokast.small { padding: 9px 15px 9px 10px; }
    svg {--svg-size: 30px;} }

  div { align-content: center }

  input {
    width: 20px !important;
    height: 20px !important;
    background: var(--c);
    color: var(--base);
    border: 0;
    padding: 0;}
    input:hover {
      background: var(--base);
      outline: 2px solid var(--c);
      color: var(--c) }

</style>