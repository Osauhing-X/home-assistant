<script>
  export let data = null;

  function tags(item){
    let {release_date, media_type} = item

    let list = []

    if(release_date) list.push(release_date)
    if(media_type) list.push(media_type)

    return list
  }
  import { base } from '$app/paths';
</script>



  <section id="collection" class="grid">
    {#await data}
      Loading Collection
    {:then data}

    <header>
      <h2>{data.name}</h2>
      <small>{data.overview}</small>
    </header>
      <div class="grid gap posters">
        {#each data.parts as item, nr}
          <a href="{base}/{item.media_type}/{item.id}" class="poster">
            <img src={data.poster_path ? `https://image.tmdb.org/t/p/w500${item.poster_path}` : ""} alt="poster" style="--height: 100px">
            <class class="grid gap">
                <h3>{item.title}</h3>
                <div class="flex gap">
                  {#each tags(item) as tag}
                    <span>{tag}</span>
                  {/each}
                </div>
              <samp class="overview">
                {item.overview}
              </samp>
            </class>
            
          </a>
        {/each}
      </div>
    {/await}
  </section>


<style>
  .overview { color: var(--reverse); }
  #collection {
    row-gap: 1em; }

  .posters {
    grid: min-content / repeat(auto-fill, minmax(250px, 1fr)) }

  .posters > a {
    text-decoration: none;
    overflow: hidden;
    display: grid; gap: 10px;
    grid-template-columns: max-content 1fr;
    background: var(--main);
    padding: 5px;
    border: 1px solid #333; }

  .posters > a h3 {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden; }

  .posters > a samp {
    display: -webkit-box;
    line-clamp: 3;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden; }
</style>