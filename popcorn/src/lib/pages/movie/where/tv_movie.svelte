<script>
  import { page, navigating } from '$app/stores';

  export let data = null
  
  function date(days){
    let plus = days > 1 || days < -1 ? true : false
    let is_old = days > 0 ? true : false

    return `${is_old ? "Released" : "It will be released in"} ${days} day${plus ? "s" : "" } ${is_old ? "ago" : ""}`
  }
</script>

<header>
  <h1>{data.title ?? data.name}</h1>
  {#if data?.release} <span title={date(data.release.days)}> {data.release.date}</span> {/if}
  {#if data?.tagline}<span title="Tagline">{data.tagline || ""}</span>{/if}
  {#if data?.runtime} <span title="Runtime">{data.runtime}</span> {/if}
</header>

<div class="grid gap images">
  <img src={data.poster_path != null ? `https://image.tmdb.org/t/p/original${data.poster_path}` : ""} alt="poster">
  {#if data.backdrop_path != null}<img src={`https://image.tmdb.org/t/p/original${data.backdrop_path}`} alt="backdrop">{/if}
</div>

<div class="flex gap">
  <!-- TRAILER -->
    {#if data?.trailer} <button on:click={()=>{window.open(data.trailer, "trailer", 'width=960,height=540');}}>
      Trailer</button>{/if}
  <!-- HOMEPAGE -->
    {#if data?.homepage} <button on:click={()=>{window.open(data.homepage, "homepage", 'width=960,height=540');}}>
      Official Site</button>{/if}
  <!-- IMDB URL -->
    {#if data?.imdb_id}
      <button on:click={()=>{window.open("https://www.imdb.com/title/"+data.imdb_id, "homepage", 'width=960,height=540');}}>
      IMDB</button>
    {/if}
</div>

    <p title="overview">{data?.overview || ""}</p>



      
      



<style lang="scss">
  .images { grid-template-columns: 3fr 8fr;}
</style>