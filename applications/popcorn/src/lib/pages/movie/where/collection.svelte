<script>
 import { t } from '$lib/assets/translations';
  import { page } from '$app/stores';
  export let data = null;
  const image = (path) => path ? `https://image.tmdb.org/t/p/w500${path}` : '';
  const year = (item) => (item.release_date || item.first_air_date || '').slice(0, 4);
  const type = (item) => item.media_type || 'movie';
  $: locale = $page.params.lang || $page.url.searchParams.get('language') || 'en';
</script>

<section class="collection-panel">
  {#await data}
    <div class="collection-loading">{$t("Loading collection…")}</div>
  {:then collection}
    <header>
      {#if collection.poster_path}<img src={image(collection.poster_path)} alt="">{/if}
      <div><span class="eyebrow">{$t("Collection")}</span><h3>{collection.name}</h3>{#if collection.overview}<p>{collection.overview}</p>{/if}</div>
    </header>
    <div class="collection-grid">
      {#each collection.parts || [] as item, index}
        <a href={`${$page.data.base}/${locale}/${type(item)}/${item.id}?language=${locale}`}>
          <div class="art">{#if item.poster_path}<img src={image(item.poster_path)} alt={item.title || item.name || ''} loading="lazy">{:else}<span>🍿</span>{/if}<i>{String(index + 1).padStart(2, '0')}</i></div>
          <div class="copy"><div class="meta">{#if year(item)}<span>{year(item)}</span>{/if}<span>{type(item)==='tv'?$t("SERIES"):$t("MOVIE")}</span></div><h4>{item.title || item.name}</h4>{#if item.overview}<p>{item.overview}</p>{/if}<b>{$t("View details")} <span>→</span></b></div>
        </a>
      {/each}
    </div>
  {/await}
</section>

<style>
  .collection-panel{min-width:0}.collection-panel>header{display:grid;grid-template-columns:76px minmax(0,1fr);gap:18px;align-items:center;padding:4px 0 20px}.collection-panel>header>img{width:76px;height:100px;object-fit:cover;border-radius:11px;box-shadow:0 12px 30px #0008}.collection-panel h3{margin:0;font-size:24px}.collection-panel header p{max-width:760px;margin:8px 0 0;color:var(--muted);font-size:13px;line-height:1.55}.collection-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(310px,100%),1fr));gap:11px}.collection-grid>a{display:grid;grid-template-columns:96px minmax(0,1fr);min-height:145px;overflow:hidden;background:linear-gradient(145deg,#1b1b21,#111116);border:1px solid var(--line);border-radius:14px;color:white;text-decoration:none}.collection-grid>a:hover{border-color:#705724;transform:translateY(-2px);box-shadow:0 16px 35px #0005}.art{position:relative;background:#202027;overflow:hidden}.art img{width:100%;height:100%;object-fit:cover}.art>span{height:100%;display:grid;place-items:center;font-size:30px}.art i{position:absolute;left:8px;top:8px;padding:4px 6px;border-radius:7px;background:#09090dcc;color:var(--gold);font-size:9px;font-style:normal;font-weight:800}.copy{display:flex;min-width:0;flex-direction:column;padding:13px}.meta{display:flex;gap:6px}.meta span{padding:3px 7px;border-radius:20px;background:#292930;color:#bbb;font-size:8px;font-weight:800;letter-spacing:.08em}.copy h4{margin:8px 0 5px;font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.copy p{display:-webkit-box;margin:0;color:var(--muted);font-size:11px;line-height:1.45;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.copy>b{margin-top:auto;padding-top:8px;color:var(--gold);font-size:10px}.copy>b span{float:right}.collection-loading{padding:30px;color:var(--muted)}@media(max-width:560px){.collection-panel>header{grid-template-columns:56px minmax(0,1fr)}.collection-panel>header>img{width:56px;height:76px}.collection-grid>a{grid-template-columns:78px minmax(0,1fr)}}
</style>
