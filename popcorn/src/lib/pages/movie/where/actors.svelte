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
        <a class="person-placeholder" href={resolve('/person/' + person.id)} aria-label={person.name}><span aria-hidden="true">♙</span><b>{person.name?.slice(0,1)}</b></a>
      {/if}
      <small>{person.name}</small>
    </div>
  {/each}
</div>


<style>
  .person { aspect-ratio: 3/5;min-width:0;overflow:hidden;border-radius:12px;background:#18181e;border:1px solid var(--line); }

  .empty{
    grid-template-rows: 1fr min-content;
    width: 100%;
  }

  .person-placeholder{position:relative;display:grid;place-items:center;min-height:0;overflow:hidden;background:radial-gradient(circle at 50% 25%,#45434d 0,#24242b 38%,#15151a 100%);text-decoration:none;color:#8d8995}.person-placeholder::after{content:"";position:absolute;width:80%;aspect-ratio:1;border-radius:50%;background:#ffffff08;bottom:-34%;left:10%}.person-placeholder span{font-size:42px;opacity:.28}.person-placeholder b{position:absolute;right:9px;bottom:9px;display:grid;place-items:center;width:25px;height:25px;border-radius:50%;background:var(--gold);color:#201605;font-size:11px;z-index:1}.person>small{padding:8px 7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

  .list {
    position: relative;
    gap: 10px;
    grid: min-content/repeat(auto-fill,minmax(var(--em, 7em),1fr));
    grid-auto-flow: row dense;
    justify-items: start; }

  @media screen and (max-width:600px) {
    .list { --em: 5em} }
</style>
