<script>
  export let json = null


  let {known_for_department, birthday, poster_path, backdrop_path, media_type, release_date, vote_average, id, title, name} = json

  let image = json?.poster_path || json?.profile_path || null
  let back = backdrop_path ? "url(https://image.tmdb.org/t/p/original" + backdrop_path + ")" : null
  let poster = image ? "https://image.tmdb.org/t/p/original" + image : null

  let {overview} = json

  let tags = []
  if(known_for_department) tags.push(known_for_department)
  if(birthday) tags.push(birthday)
  if(media_type) tags.push(media_type)
  if(release_date) tags.push(release_date)
  if(vote_average) tags.push(vote_average)
  
  import { resolve } from '$app/paths';
</script>

<section style="--backdrop: {back}">
  
  <a class="grid" href={resolve("/" + media_type + "/" + id)}>
    <img src={poster} alt="poster">

    <div>
      <div class="flex wrap" style="justify-content: space-between;">
        <b style="font-size: xx-large;">{title ?? name}</b>
        <div class="flex wrap gap _2" style="height:min-content">
          {#each tags as tag}
            <span>{tag}</span>
          {/each}
        </div>
      </div>
    
      <p>{overview}</p>

      <hr>

      <button>View</button>
    </div>
  </a>
</section>

<style lang="scss">
  b { color: #fff !important;}
  p { color: #999 !important;}
  section {
    box-shadow: inset 0 0 5em 5em var(--base), inset 0 0 2em 2em var(--base);
    background: var(--backdrop);
    background-size: cover;
    padding: var(--padding, 3em);
    display: flex; gap: 1em ;
    position: relative;
    margin: -1em 0;

    &::before {
      content: "";
      position: absolute;
      top: 0; left: 0;
      height: 100%;  width: 100%;
      backdrop-filter: blur(10px);
    }

    @media (min-width: 800px){
      --padding: 7em 5em }
    @media (max-width: 600px){
      --padding: 0 1em;
      img {display: none} }

    > a.grid {
      text-decoration: none;
      grid: "poster content" min-content / min-content 1fr; gap: 1em;
      max-width: 600px;
      > img {grid-area: poster; min-width: 8em;}
      > div {grid-area: content;}

      backdrop-filter: blur(1em) brightness(.2);
      padding: 1em;
    }
  }
</style>