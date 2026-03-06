<script>
  import { resolve } from '$app/paths';
  export let data = null;

  let mode = 'posters'

  import Card from "$lib/pages/movie/components/poster.svelte"
</script>



<div class='grid list'>
  {#each data as person, nr}
    <div class="grid person" class:empty={!person?.profile_path} title={person.character}>
      {#if person.profile_path}
        <Card object={person} />
      {:else}
        <a href={resolve('/person/' + person.id)} aria-label="person"> </a>
      {/if}
      <small>{person.name}</small>
    </div>
  {/each}
</div>


<style>
  .person { aspect-ratio: 3/5; }

  .empty{
    grid-template-rows: 1fr min-content;
    width: 100%;
  }

  .empty > a {
    display: block;
    animation: blink 2s linear infinite;
    position: relative;
  }

  .empty > a::after{
    content: "?";
    color: var(--reverse);
    font-size: xxx-large;
    font-family: 'extaas';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  @keyframes blink {
    0%, 100% {background-color: #666;}
    50% {background-color: #888;}
  }

  .list {
    position: relative;
    gap: 10px;
    grid: min-content/repeat(auto-fill,minmax(var(--em, 7em),1fr));
    grid-auto-flow: row dense;
    justify-items: start; }

  @media screen and (max-width:600px) {
    .list { --em: 5em} }
</style>