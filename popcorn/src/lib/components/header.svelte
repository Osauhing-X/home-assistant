<script>
  import { page } from '$app/stores';
  import {language} from '$lib/config';
  import {onMount} from 'svelte';
  import {goto} from '$app/navigation';
  $: where = $page.params.where;
  const labels={et:{discover:'Avasta',search:'Otsi',saved:'Mina & pere',aria:'Filmiportaal'},en:{discover:'Discover',search:'Search',saved:'Me & family',aria:'Movie portal'}};$:copy=labels[$language]||labels.et;
  onMount(()=>{$language=['et','en'].includes($page.params.lang)?$page.params.lang:(localStorage.getItem('popcorn:language')||localStorage.getItem('save:language')||'et')});function setLanguage(value){$language=value;localStorage.setItem('popcorn:language',value);localStorage.setItem('save:language',value);const url=new URL($page.url);const base=$page.data.base||'';let path=url.pathname.slice(base.length)||'/';const parts=path.split('/').filter(Boolean);if(['et','en'].includes(parts[0]))parts[0]=value;else parts.unshift(value);url.searchParams.set('language',value);goto(`${base}/${parts.join('/')}${url.search}`,{replaceState:true,noScroll:true,keepFocus:true})}
</script>

<header class="portal-header">
  <a class="portal-brand" href={$page.data.base + '/' + ($page.params.lang||$language)} aria-label="Popcorn avaleht">
    <span class="popcorn-mark" aria-hidden="true">🍿</span>
    <span><b>Popcorn</b><small>OSAÜHING X</small></span>
  </a>
  <nav aria-label={copy.aria}>
    <a href={$page.data.base + '/' + ($page.params.lang||$language)}>{copy.discover}</a>
    <a href={$page.data.base + '/' + ($page.params.lang||$language) + '/s_all' + $page.url.search}>{copy.search}</a>
    <a href={$page.data.base + '/' + ($page.params.lang||$language) + '/?view=saved&language=' + $language}>{copy.saved}</a>
  </nav>
  <div class="header-tools"><slot /><select value={$language} on:change={(e)=>setLanguage(e.currentTarget.value)} aria-label="Portaali keel"><option value="et">ET</option><option value="en">EN</option></select></div>
</header>

<style>
  .portal-header{min-width:0;display:flex;align-items:center;gap:24px;padding:12px max(16px,5vw);border-bottom:1px solid var(--line);background:rgba(9,9,13,.92);backdrop-filter:blur(18px);position:sticky;top:0;z-index:30}
  .portal-brand{display:flex;align-items:center;gap:10px;color:var(--ink);text-decoration:none;flex:0 0 auto}.popcorn-mark{width:36px;height:36px;display:grid;place-items:center;background:#202027;border:1px solid var(--line);border-radius:10px;font-size:21px}.portal-brand b{display:block;font-size:17px}.portal-brand small{display:block;font-size:8px;letter-spacing:.15em;color:var(--gold)}
  nav{display:flex;align-items:center;gap:5px;min-width:0;overflow-x:auto;scrollbar-width:none}nav a,nav button{white-space:nowrap;color:var(--muted);text-decoration:none;background:transparent;border:0;border-radius:9px;padding:9px 11px;cursor:pointer;font-weight:700;font-size:12px}nav a:hover,nav button:hover,nav .liked{color:var(--ink);background:var(--panel2)}nav .liked{color:var(--gold)}
  .header-tools{margin-left:auto;min-width:0;display:flex;gap:8px;align-items:center}.header-tools select{background:#17171c;color:white;border:1px solid var(--line);border-radius:8px;padding:8px}
  @media(max-width:700px){.portal-header{align-items:flex-start;gap:10px;flex-wrap:wrap}.popcorn-mark{width:32px;height:32px}.portal-header nav{order:3;width:100%}.header-tools{max-width:60%}.portal-brand small{display:none}}
</style>
