<script>
  import { page, navigating } from '$app/stores';

  // Imports
  import Persons from "$lib/movie/where/actors.svelte";
  import Recommendations from "$lib/movie/where/recommendations.svelte";
  import Collection from "$lib/movie/where/collection.svelte";
  import Seasons from "$lib/movie/where/seasons.svelte";
  import TvMovie from "$lib/movie/where/tv_movie.svelte";
  import Providers from "$lib/movie/where/providers.svelte";
  import MyLinks from "$lib/movie/where/your_links.svelte";
  import PersonData from "$lib/movie/where/person_data.svelte";

  import { save, view } from '$lib/movie/discover_store.js';

  import Back from "$lib/movie/image/back.svg?raw";
  import Share from "$lib/movie/image/share.svg?raw";
  import Like from "$lib/movie/image/like.svg?raw";
  

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
  import { onMount } from 'svelte';
  let i18n = get_i18n($page.data.meta, '/discover/[what]/[where]');
  import { base } from '$lib/config.js'
</script>

<svelte:head>
  <meta property="og:type" content="video.other" />
</svelte:head>

{#if !$navigating}
  <center class="padding top bottom grid gap _5">
    <section class="flex wrap gap">
      <a class="null flex" href={$base}>
        {@html Back} {$i18n?.back}
      </a>
      <button 
        class="null flex" 
        class:like={$view?.[$page.params.what]?.includes(id)} 
        on:click={() => save($page.params.what,'save', id)}
      >
        {@html Like} {$i18n?.like}
      </button>
      <button 
        class="null flex" 
        on:click={() => navigator.share({ url: $page.url.origin + $page.url.pathname })}
      >
        {@html Share} {$i18n?.share}
      </button>
    </section>

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
            {$i18n[element.id]}
            </center>
          </summary>
          <center>
          <div>
            <svelte:component this={element.import} data={element.json} i18n={get_i18n($page.data.meta, element.id)} />
          </div>
        </center>
      </details>
    {/each}
  </section>
{/if}

<style lang="scss">
  details {
    background: var(--transparent);
    > center > div {
      padding: 1em;
    }
  }

  .null {
    background: var(--transparent);
    border: 0;
    padding: 5px 15px 5px 10px;
    line-height: 10px;
    max-height: 30px;
    gap: 10px;
    align-items: center;
    font-family: 'extaas';
    font-size: 14px;
  }

  a {
    color: var(--reverse) !important;
    text-decoration: none;
  }

  .null:hover {
    outline: 1px solid var(--primary);
  }

  .like {
    --like: red;
  }
</style>
