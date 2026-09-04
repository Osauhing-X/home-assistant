<script>
 import PortalFooter from "$lib/components/footer.svelte";
 import { t } from '$lib/assets/translations';
  import {onMount} from 'svelte';import {view,fav} from '$lib/pages/movie/scripts/favorite';import Header from '$lib/components/header.svelte';import Card from '$lib/pages/movie/components/poster.svelte';let loaded={};onMount(async()=>{fav().get();const source=$view||{};for(const type of ['movie','tv','person']){loaded[type]=[];for(const id of source[type]||[]){const response=await fetch(`@_movie/solo`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({what:type,id})});if(response.ok)loaded[type]=[...loaded[type],await response.json()]}}loaded={...loaded}});
</script>
<Header/><main class="movie-shell"><span class="eyebrow">{$t("On this device")}</span><h1 class="movie-title">{$t("Favorites")}</h1><p class="movie-lead">{$t("Your locally saved movies, series and people.")}</p>{#each Object.entries(loaded) as [type,items]}{#if items.length}<section class="movie-section"><h2>{type==='tv'?$t("Series"):type==='person'?$t("People"):$t("Movies")}</h2><div class="movie-grid">{#each items as object}<Card {object} show={false}/>{/each}</div></section>{/if}{/each}{#if !Object.values(loaded).flat().length}<div class="empty-state">{$t("You have not added any favorites yet.")}</div>{/if}</main>
<PortalFooter/>
