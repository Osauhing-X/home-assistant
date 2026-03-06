<script>
  import { page, navigating } from '$app/stores';

  // Imports
  import Persons from "$lib/pages/movie/where/actors.svelte";
  import Recommendations from "$lib/pages/movie/where/recommendations.svelte";
  import Collection from "$lib/pages/movie/where/collection.svelte";
  import Seasons from "$lib/pages/movie/where/seasons.svelte";
  import TvMovie from "$lib/pages/movie/where/tv_movie.svelte";
  import Providers from "$lib/pages/movie/where/providers.svelte";
  import MyLinks from "$lib/pages/movie/where/your_links.svelte";
  import PersonData from "$lib/pages/movie/where/person_data.svelte";

  import { fav, view } from '$lib/pages/movie/scripts/favorite';


  

  // Kasuta $page.data
  $: data = $page.data;

  // Põhiväljad
  $: ({ 
    original_title, original_name, name, overview, tagline, 
    poster_path, backdrop_path, release, id, persons, 
    similar, collection, seasons, providers 
  } = data);

  $: title = original_title || original_name || name;

  // Komponentide jaotus
  $: top = (() => {
    let arr = [];
    if (['tv', 'movie'].includes($page.params.what)) {
      arr.push({
        import: TvMovie,
        json: Object.fromEntries(
          Object.entries(data).filter(([key]) => 
            ['id','title','name','overview','release','tagline','runtime',
             'backdrop_path','poster_path','homepage','trailer'].includes(key)
          )
        )
      });
    }
    if ($page.params.what === 'person') {
      arr.push({ import: PersonData, json: data });
    }
    if (collection) {
      arr.push({ import: Collection, json: collection });
    }
    return arr;
  })();

  $: middle = (() => {
    let arr = [];
    if (seasons) arr.push({ import: Seasons, json: seasons, id: 'season' });
    if (['tv', 'movie'].includes($page.params.what)) {
      arr.push({ import: MyLinks, json: title, id: 'links' });
    }
    if (providers?.languages?.length > 0) {
      arr.push({ import: Providers, json: { providers, title }, id: 'providers' });
    }
    if (persons) arr.push({ import: Persons, json: persons, id: 'actors' });
    if (similar) arr.push({ import: Recommendations, json: similar, id: 'similar' });
    return arr;
  })();

  // SEO
  $: seo_json = {
    title: `${title}${tagline ? " - " + tagline : ""}`,
    description: overview,
    keywords: `${$page.params.what}, Trailer, Recommendations, Tagline, Description`,
    image: `https://image.tmdb.org/t/p/original${backdrop_path}`
  };



  // Keelepakett -> $i18n
  import { get_i18n } from '$lib/assets/language.js';
  let i18n = get_i18n($page.data.meta, '/discover/[what]/[where]');


  
  // Language
  import language_pack from '$lib/pages/movie/i18n.yaml'
  import { request } from '$lib/assets/request'
  let details = request('where_details', language_pack)


  // Imports
  import Header from '$lib/components/header.svelte';
</script>

<svelte:head>
  <meta property="og:type" content="video.other" />
</svelte:head>

{#if !$navigating}
  <Header />

  <center css class="padding top bottom grid gap _5">
    {#each top as element}
      <section class="grid gap _2">
        <svelte:component this={element.import} data={element.json} i18n={get_i18n($page.data.meta, element.id)} />
      </section>
    {/each}
  </center>

  <section class="bottom">
    {#each middle as element}
      <details name="list" class="black">
        <summary>
          <center>
            {$details[element.id]}
          </center>
        </summary>
        <center>
          <svelte:component this={element.import} data={element.json} i18n={get_i18n($page.data.meta, element.id)} />
        </center>
      </details>
    {/each}
  </section>
{/if}

<style lang="scss">
  details {
    background: #eee;
    > summary {
      background: #000;
      list-style: none;
      padding: 5px;
      color: #fff; }

    > center {
      padding: 1em 0; }

    + details {
      margin-top: 10px; }
  }




</style>
