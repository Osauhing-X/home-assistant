<script>
  import { page } from '$app/stores'
  import { onMount } from 'svelte'
  import { language } from '$lib/assets/language.js'
  import { base } from '$lib/config.js'

  let params = new URLSearchParams($page.url.search)

  let what = params.get("api") ? atob(params.get("api")) : "trending/all/day"

  let deafult_params = {
    language: params.get("language") || "en",
    page: params.get("page") || 1,
    fetch: params.get("fetch") || 3
  }

  let query = params.get("query") || ""
  let sort_by = params.get("sort_by") || "popularity.desc"
  let with_genres

  let languages = []
  let genres = []

  async function imdb(what, value = null, lang = null) {
    const res = await fetch($base + '@_movie/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ what, value, lang })
    })

    const text = await res.text()

    if (!res.ok) {
      console.error('TMDB fetch failed', text)
      throw new Error('TMDB fetch failed')
    }

    return JSON.parse(text)
  }

  onMount(async () => {
    languages = await imdb('languages')

    if (what?.includes('discover')) {
      genres = await imdb(
        'genres',
        ['tv', 'movie'].find(word => what.includes(word)),
        deafult_params.language
      )
    }
  })

  $: if (what?.includes('discover')) {
    imdb(
      'genres',
      ['tv', 'movie'].find(word => what.includes(word)),
      deafult_params.language
    ).then(r => genres = r)
  }

  function api() {
    let params = { ...deafult_params }

    if (what?.includes('search') && query) params.query = query
    else if (what?.includes('discover')) params.sort_by = sort_by

    if (what?.includes('discover') && with_genres)
      params.with_genres = with_genres

    let api_params = new URLSearchParams(params).toString()
    let api_url = $page.url.pathname + `?api=${btoa(what)}&${api_params}`

    window.location.href = $base + api_url
  }

  $: search = what.includes('search')
  $: search, deafult_params.page = 1

  import loop from "$lib/movie/search.svg?raw"

  let show = false
  export let i18n = null
</script>

<section>
  <label class="flex search">
    {@html loop}
    <input type="checkbox" bind:checked={show}>
  </label>

  <form on:submit|preventDefault={api} class="grid gap" class:hidden={!show}>

    <input type="button" value="✖" on:click={() => show = false} class="close">

    <label>{$i18n?.type}
      <select bind:value={what}>

        <optgroup label={$i18n?.all[0]}>
          <option value="trending/all/day">{$i18n?.all[1]}</option>
          <option value="search/multi">{$i18n?.all[2]}</option>
        </optgroup>

        <optgroup label={$i18n?.movie[0]}>
          <option value="trending/movie/day">{$i18n?.movie[1]}</option>
          <option value="discover/movie">{$i18n?.movie[2]}</option>
          <option value="movie/upcoming">{$i18n?.movie[3]}</option>
          <option value="movie/popular">{$i18n?.movie[4]}</option>
          <option value="movie/top_rated">{$i18n?.movie[5]}</option>
          <option value="movie/now_playing">{$i18n?.movie[6]}</option>
          <option value="search/movie">{$i18n?.movie[7]}</option>
        </optgroup>

        <optgroup label={$i18n?.tv[0]}>
          <option value="trending/tv/day">{$i18n?.tv[1]}</option>
          <option value="discover/tv">{$i18n?.tv[2]}</option>
          <option value="search/tv">{$i18n?.tv[3]}</option>
        </optgroup>

      </select>
    </label>

    <label>{$i18n?.nr}
      <input type="number" bind:value={deafult_params.page} required disabled={search}>
    </label>

    {#if languages.length}
      <label>{$i18n?.lang}
        <input list="languages" bind:value={deafult_params.language}>
        <datalist id="languages">
          {#each languages as code}
            <option value={code}>
              {new Intl.DisplayNames([$language || 'en'], { type: "language" }).of(code)}
            </option>
          {/each}
        </datalist>
      </label>
    {/if}

    <label>{$i18n?.fetch}
      <input type="number" bind:value={deafult_params.fetch} required>
    </label>

    {#if search}

      <label>{$i18n?.search}
        <input bind:value={query} type="search" required>
      </label>

    {:else if what?.includes('discover')}

      <label>{$i18n?.sort[0]}>
        <select bind:value={sort_by}>
          <option value="popularity.desc">{$i18n?.sort[1]}</option>
          <option value="vote_average.desc">{$i18n?.sort[2]}</option>
          <option value="vote_count.desc">{$i18n?.sort[3]}</option>
        </select>
      </label>

      {#if genres.length}
        <label>{$i18n?.genre}
          <select bind:value={with_genres} multiple>
            {#each genres as option}
              <option value={option.value}>{option.title}</option>
            {/each}
          </select>
        </label>
      {/if}

    {/if}

    <input type="submit">
  </form>
</section>


<style lang="scss">
  

  

  section {
    position: relative;
    z-index: 10;
  }



  form {
    margin-top: .7em;
    margin-left: -.3em;
    position: absolute;
    background: var(--body);
    border: 1px solid var(--black);
    border-radius: 5px;
    padding: 10px;
    box-shadow: 0 1em 20px 20px #000;

    &.hidden {display: none;}

    .close {
      background: transparent;
      border: 0px;
      width: min-content;
      position: absolute;
      top: 1px;
      right: 0px;
      cursor: pointer;
    }
  }

  label:not(.search){
    display: grid;
    font-family: monospace;
    gap: 5px;
  }

  label.search {
    transition: .5s;
    position: relative;
    padding: 0.38em;
    border: 1px solid var(--transparent);

    &:hover {
      background: var(--transparent);
      border: 1px solid #aaa; }

    > input {
      position: absolute;
      visibility: hidden; }
  }

  section:has(input:checked) > label.search {
    background: var(--transparent);
    border-color: var(--primary);
  }



</style>