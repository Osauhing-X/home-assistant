<script>
  import { page } from '$app/stores';
  import Header from '$lib/components/header.svelte';
  import Persons from '$lib/pages/movie/where/actors.svelte';
  import Recommendations from '$lib/pages/movie/where/recommendations.svelte';
  import Collection from '$lib/pages/movie/where/collection.svelte';
  import Seasons from '$lib/pages/movie/where/seasons.svelte';
  import Providers from '$lib/pages/movie/where/providers.svelte';
  import MyLinks from '$lib/pages/movie/where/your_links.svelte';
  import PersonData from '$lib/pages/movie/where/person_data.svelte';
  import language_pack from '$lib/pages/movie/i18n.yaml';
  import { request } from '$lib/assets/request';
  let details=request('where_details',language_pack);
  $: data=$page.data||{};
  $: title=data.title||data.name||data.original_title||data.original_name||'Popcorn';
  $: poster=data.poster_path||data.profile_path;
  $: image=poster?`https://image.tmdb.org/t/p/original${poster}`:null;
  $: backdrop=data.backdrop_path?`https://image.tmdb.org/t/p/original${data.backdrop_path}`:image;
  $: sections=[
    data.collection&&{id:'collection',component:Collection,value:data.collection},
    data.seasons?.length&&{id:'season',component:Seasons,value:data.seasons},
    ['movie','tv'].includes($page.params.what)&&{id:'links',component:MyLinks,value:title},
    data.providers?.languages?.length&&{id:'providers',component:Providers,value:{providers:data.providers,title}},
    data.persons?.length&&{id:'actors',component:Persons,value:data.persons},
    data.similar?.length&&{id:'similar',component:Recommendations,value:data.similar},
    $page.params.what==='person'&&{id:'credits',component:PersonData,value:data}
  ].filter(Boolean);
</script>
<svelte:head><title>{title} · Popcorn</title><meta name="description" content={data.overview||data.biography||'Popcorn by Osaühing X'}></svelte:head>
<Header />
<main class="movie-shell">
  <article class="detail-hero" style={`--backdrop:url('${backdrop||''}')`}>
    <div class="detail-content">
      {#if image}<img class="detail-poster" src={image} alt={title}>{:else}<div></div>{/if}
      <div class="detail-copy"><span class="eyebrow">{$page.params.what==='tv'?'Sari':$page.params.what==='person'?'Persoon':'Film'}</span><h1>{title}</h1><div class="meta-row">{#if data.release?.date}<span>{data.release.date}</span>{/if}{#if data.runtime}<span>{data.runtime}</span>{/if}{#if data.known_for_department}<span>{data.known_for_department}</span>{/if}{#if data.vote_average}<span>★ {data.vote_average.toFixed(1)}</span>{/if}</div>{#if data.tagline}<p><b>{data.tagline}</b></p>{/if}<p>{data.overview||data.biography||''}</p></div>
    </div>
  </article>
  <div class="detail-save"><div class="action-row">{#if data.trailer}<a href={data.trailer} target="_blank" rel="noreferrer">Vaata treilerit ↗</a>{/if}{#if data.homepage}<a href={data.homepage} target="_blank" rel="noreferrer">Ametlik leht ↗</a>{/if}</div><a class="primary" href={`${$page.data.base}/?saveId=${data.id}&saveType=${$page.params.what}&saveTitle=${encodeURIComponent(title)}&savePoster=${encodeURIComponent(data.poster_path||data.profile_path||'')}`}>Salvesta</a></div>
  {#if sections.length}<div class="detail-sections">{#each sections as section}<details><summary>{details?.[section.id]||section.id}</summary><div class="detail-body"><svelte:component this={section.component} data={section.value}/></div></details>{/each}</div>{/if}
</main>
