<script>
  import { page } from '$app/stores';
  import { view } from '$lib/pages/movie/scripts/favorite';
  export let object=null;export let show=true;
  $: path=object?.poster_path||object?.profile_path;
  $: type=object?.media_type||($page.params.what==='tv'?'tv':'movie');
  $: liked=show&&($view?.[type]||[]).map(String).includes(String(object?.id));
</script>
{#if object&&path}<a class="poster-card" href={`${$page.data.base}/${type}/${object.id}${$page.url.searchParams.get('language')?`?language=${$page.url.searchParams.get('language')}`:''}`} aria-label={object.title||object.name||'Vaata'}><img src={`https://image.tmdb.org/t/p/w500${path}`} alt={object.title||object.name||''} loading="lazy">{#if liked}<span class="liked">♥</span>{/if}</a>{/if}
<style>.poster-card{display:block;position:relative;width:100%;aspect-ratio:2/3;overflow:hidden;border-radius:13px;background:#1b1b21}.poster-card img{display:block;width:100%;height:100%;object-fit:cover;transition:.3s}.poster-card:hover img{transform:scale(1.04);filter:brightness(.78)}.liked{position:absolute;right:8px;top:8px;background:#09090dcc;color:var(--gold);padding:5px 8px;border-radius:20px}</style>
