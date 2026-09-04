<script>
 import PortalFooter from "$lib/components/footer.svelte";
 import { t } from '$lib/assets/translations';
  import Header from '$lib/components/header.svelte';import Search from '$lib/pages/movie/what/search.svelte';import SelectPage from '$lib/pages/movie/what/select_page.svelte';import Card from '$lib/pages/movie/components/poster.svelte';import {request} from '$lib/assets/request';export let data;
</script>
<Header><Search i18n={request('what_search')}/></Header>
<main class="movie-shell"><div class="search-header"><div><span class="eyebrow">{$t("Popcorn catalog")}</span><h1 class="movie-title">{$t("Discover movies and series")}</h1></div><button class="primary" popovertarget="search_popover">{$t("Filters and search")}</button></div>{#if data?.data?.length}<div class="movie-grid">{#each data.data as object}<Card {object}/>{/each}</div><SelectPage json={data.pages}/>{:else}<div class="empty-state">{$t("No results found. Try another search.")}</div>{/if}</main>
<PortalFooter/>
