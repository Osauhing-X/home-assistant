<script>
  import Header from '$lib/components/header.svelte';import Search from '$lib/pages/movie/what/search.svelte';import SelectPage from '$lib/pages/movie/what/select_page.svelte';import Card from '$lib/pages/movie/components/poster.svelte';import language_pack from '$lib/pages/movie/i18n.yaml';import {request} from '$lib/assets/request';export let data;
</script>
<Header><Search i18n={request('what_search',language_pack)}/></Header>
<main class="movie-shell"><div class="search-header"><div><span class="eyebrow">Popcorn kataloog</span><h1 class="movie-title">Avasta filme ja sarju</h1></div><button class="primary" popovertarget="search_popover">Filtrid ja otsing</button></div>{#if data?.data?.length}<div class="movie-grid">{#each data.data as object}<Card {object}/>{/each}</div><SelectPage json={data.pages}/>{:else}<div class="empty-state">Tulemusi ei leitud. Proovi teist otsingut.</div>{/if}</main>
