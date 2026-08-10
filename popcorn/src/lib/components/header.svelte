<script>
  import { page } from '$app/stores';
  import { fav, view } from '$lib/pages/movie/scripts/favorite';
  $: what = $page.params.what;
  $: where = $page.params.where;
  $: liked = Boolean($view?.[what]?.includes(String(where)) || $view?.[what]?.includes(JSON.stringify(where)));
</script>

<header class="portal-header">
  <a class="portal-brand" href={$page.data.base + '/'} aria-label="Popcorn avaleht">
    <img src={$page.data.base + '/logo.png'} alt="">
    <span><b>Popcorn</b><small>OSAÜHING X</small></span>
  </a>
  <nav aria-label="Filmiportaal">
    <a href={$page.data.base + '/'}>Avasta</a>
    <a href={$page.data.base + '/s_all' + $page.url.search}>Otsi</a>
    <a href={$page.data.base + '/favorite'}>Lemmikud</a>
    {#if where}
      <button popovertarget="new_date">Lisa kuupäev</button>
      <button class:liked on:click={() => fav().save(what, where)}>{liked ? '♥ Salvestatud' : '♡ Salvesta'}</button>
    {/if}
  </nav>
  <div class="header-tools"><slot /></div>
</header>

<style>
  .portal-header{min-width:0;display:flex;align-items:center;gap:24px;padding:12px max(16px,5vw);border-bottom:1px solid var(--line);background:rgba(9,9,13,.92);backdrop-filter:blur(18px);position:sticky;top:0;z-index:30}
  .portal-brand{display:flex;align-items:center;gap:10px;color:var(--ink);text-decoration:none;flex:0 0 auto}.portal-brand img{width:36px;height:36px;object-fit:contain;border-radius:9px}.portal-brand b{display:block;font-size:17px}.portal-brand small{display:block;font-size:8px;letter-spacing:.15em;color:var(--gold)}
  nav{display:flex;align-items:center;gap:5px;min-width:0;overflow-x:auto;scrollbar-width:none}nav a,nav button{white-space:nowrap;color:var(--muted);text-decoration:none;background:transparent;border:0;border-radius:9px;padding:9px 11px;cursor:pointer;font-weight:700;font-size:12px}nav a:hover,nav button:hover,nav .liked{color:var(--ink);background:var(--panel2)}nav .liked{color:var(--gold)}
  .header-tools{margin-left:auto;min-width:0}.header-tools:empty{display:none}
  @media(max-width:700px){.portal-header{align-items:flex-start;gap:10px;flex-wrap:wrap}.portal-brand img{width:32px;height:32px}.portal-header nav{order:3;width:100%}.header-tools{max-width:60%}.portal-brand small{display:none}}
</style>
