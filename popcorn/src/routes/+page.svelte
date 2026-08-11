<script>
  import { base } from '$app/paths';
  import { onMount } from 'svelte';
  import FamilyCalendar from '$lib/pages/calender/family_calendar.svelte';
  import { language } from '$lib/config';

  let tab = 'discover', movies = [], loading = true, busy = false, family = { events: [], folders: [], settings: { notifyServices: [] } };
  let ha = { connected: false, people: [], controls: [], notifyServices: [] }, local = [], query = '', scope = 'local', supportOpen = false, editorOpen = false, folderOpen = false;
  let draft = blank(), folderDraft = blankFolder(), toast = '', savedFilter = '', savedSort = 'new', selectedMonth = '', activeFolder = null;
  function image(path) { return path ? `https://image.tmdb.org/t/p/w500${path}` : ''; }
  const today = new Date().toISOString().slice(0, 10);
  const days = (date) => Math.ceil((new Date(`${date}T12:00:00`) - new Date()) / 86400000);
  function blank(movie = {}) { return { tmdbId: movie.id || null, mediaType: movie.media_type || 'movie', title: movie.title || movie.name || '', image: image(movie.poster_path), date: movie.release_date || movie.first_air_date || '', note: '', folderId: '' }; }
  function blankFolder() { return { name: '', room: '', members: [], notifyServices: [], entities: [] }; }
  function flash(value) { toast = value; setTimeout(() => toast = '', 2600); }

  onMount(async () => {
    try { local = JSON.parse(localStorage.getItem('popcorn:personal') || '[]'); } catch { local = []; }
    const params=new URLSearchParams(location.search);tab=params.get('view')||tab;$language=localStorage.getItem('popcorn:language')||'et';
    await Promise.all([loadMovies(), loadFamily()]); loading = false;
    if(params.get('saveId')){openSave({id:params.get('saveId'),media_type:params.get('saveType')||'movie',title:params.get('saveTitle')||'',poster_path:params.get('savePoster')||null});history.replaceState({},'',base+'/');}
  });
  async function loadMovies() {
    try { const r = await fetch(`${base}/@_movie/json?api=dHJlbmRpbmcvYWxsL3dlZWs=&include_adult=false&language=${$language}&fetch=2&page=1`); movies = (await r.json()).data || []; }
    catch { movies = []; }
  }
  async function search() {
    if (!query.trim()) return loadMovies(); loading = true;
    const encoded = btoa(`search/multi`);
    try { const r = await fetch(`${base}/@_movie/json?api=${encoded}&query=${encodeURIComponent(query)}&include_adult=false&language=et-EE&fetch=1&page=1`); movies = (await r.json()).data || []; } finally { loading = false; }
  }
  async function loadFamily() {
    try { const r = await fetch(`${base}/@_popcorn/family`); const data = await r.json(); family = data.store; ha = data.ha; }
    catch { flash('Pereandmeid ei saanud laadida'); }
  }
  function openSave(movie = {}) { draft = blank(movie); scope = 'local'; editorOpen = true; }
  async function save() {
    if (!draft.title.trim()) return; busy = true;
    try {
      if (scope === 'local') {
        const item = { ...draft, id: crypto.randomUUID(), createdAt: new Date().toISOString() };
        local = [item, ...local]; localStorage.setItem('popcorn:personal', JSON.stringify(local));
      } else {
        const r = await fetch(`${base}/@_popcorn/family`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ action: 'save', item: draft }) });
        family = (await r.json()).store;
      }
      editorOpen = false; flash(scope === 'local' ? 'Lisatud sinu nimekirja' : 'Lisatud pere nimekirja');
    } finally { busy = false; }
  }
  async function remove(item, familyItem) {
    if (familyItem) { const r = await api({ action: 'remove', id: item.id }); family = r.store; }
    else { local = local.filter((x) => x.id !== item.id); localStorage.setItem('popcorn:personal', JSON.stringify(local)); }
    flash('Eemaldatud');
  }
  async function api(payload) { const r = await fetch(`${base}/@_popcorn/family`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }); if (!r.ok) throw new Error('Request failed'); return r.json(); }
  async function saveFolder() { busy = true; try { const r = await api({ action: 'folder', folder: folderDraft }); family = r.store; folderOpen = false; folderDraft = blankFolder(); flash('Kaust salvestatud'); } finally { busy = false; } }
  async function saveSettings() { busy = true; try { const r = await api({ action: 'settings', settings: family.settings }); family = r.store; flash('Teavituste seaded salvestatud'); } finally { busy = false; } }
  async function lightsOff(folder) { busy = true; try { await api({ action: 'lightsOff', id: folder.id }); flash(`${folder.room || folder.name}: tuled kustutatud`); } catch { flash('Home Assistant ei vastanud'); } finally { busy = false; } }
  async function toggleEntities(folder,entities=folder.entities||[]) { busy=true;try{const data=await api({action:'toggleEntities',id:folder.id,entities});ha=data.ha;flash(entities.length===1?'Seade lülitatud':'Kausta seadmed lülitatud')}catch{flash('Home Assistant ei vastanud')}finally{busy=false} }
  function changeLanguage(value){$language=value;localStorage.setItem('popcorn:language',value);loadMovies();}
  const translations={et:{discover:'Avasta',catalog:'Kataloog',saved:'Mina & pere',folders:'Kaustad',settings:'Seaded',hero:'Leia midagi, mida tasub oodata.',lead:'Avasta filme ja sarju, salvesta endale või jaga kogu perega.',search:'Otsi filmi või sarja…',popular:'Valik sulle'},en:{discover:'Discover',catalog:'Catalog',saved:'Me & family',folders:'Folders',settings:'Settings',hero:'Find something worth waiting for.',lead:'Discover movies and series, save privately or share with the family.',search:'Search movies or series…',popular:'Picked for you'}};
  $: ui=translations[$language]||translations.et;
  function toggle(list, value) { return list.includes(value) ? list.filter((x) => x !== value) : [...list, value]; }
  function sorted(list){const q=savedFilter.toLocaleLowerCase();const filtered=list.filter(x=>(!q||x.title?.toLocaleLowerCase().includes(q)||family.folders.find(f=>f.id===x.folderId)?.name?.toLocaleLowerCase().includes(q))&&(!selectedMonth||x.date?.startsWith(selectedMonth)));return [...filtered].sort((a,b)=>{if(savedSort==='az')return a.title.localeCompare(b.title);if(savedSort==='za')return b.title.localeCompare(a.title);if(savedSort==='unreleased'){const now=Date.now(),ad=a.date?new Date(a.date).getTime():Infinity,bd=b.date?new Date(b.date).getTime():Infinity;return (ad<now)-(bd<now)||ad-bd}const ad=new Date(a.date||a.createdAt||0),bd=new Date(b.date||b.createdAt||0);return savedSort==='old'?ad-bd:bd-ad})}
  $: visible = movies.filter((x) => x.poster_path && (x.title || x.name));
  $: filteredLocal=sorted(local);$: filteredFamily=sorted(family.events);
</script>

<svelte:head><title>Popcorn · Osaühing X</title><meta name="theme-color" content="#09090d"></svelte:head>
<style>
  .settings-card { max-width: 760px; margin: 28px auto; padding: 28px; border: 1px solid var(--line); border-radius: 18px; background: var(--panel); }
  .settings-card h2 { margin: 0; font-size: 24px; }
  .settings-card > p { color: var(--muted); line-height: 1.6; }
  .settings-card .checks { margin: 22px 0; }
  .settings-card code { color: var(--gold); }
  .nav-link{color:var(--muted);text-decoration:none;padding:10px 15px;border-radius:10px;font-weight:600}.nav-link:hover{background:#202027;color:white}.language{background:#17171c;color:white;border:1px solid var(--line);border-radius:9px;padding:8px}
  .saved-tools{display:grid;grid-template-columns:minmax(0,1fr) minmax(190px,280px);gap:12px;margin:26px 0 14px}.saved-tools label{display:grid;gap:6px;color:var(--muted);font-size:11px}.saved-tools input,.saved-tools select{background:var(--panel);color:white;border:1px solid var(--line);padding:12px;border-radius:11px}.section-rule{margin:28px 0;border:0;border-top:1px solid var(--line)}
  .saved{grid-template-columns:minmax(0,1fr) 40px}.saved-link{display:grid;grid-template-columns:60px minmax(0,1fr);align-items:center;gap:14px;text-decoration:none;color:inherit;min-width:0}.folder-open{display:grid;grid-template-columns:46px minmax(0,1fr) 30px;gap:12px;align-items:center;width:100%;padding:0;background:none;border:0;color:inherit;text-align:left;cursor:pointer}.folder-open .folder-icon{margin:0}.folder.expanded{grid-column:1/-1}.folder-movies{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin:16px 0}.device-list{display:grid;gap:7px;margin:14px 0}.device-toggle{display:flex;align-items:center;justify-content:space-between;border:1px solid var(--line);background:#101014;color:var(--muted);border-radius:9px;padding:9px 11px;cursor:pointer}.device-toggle i{width:32px;height:18px;background:#333;border-radius:20px;position:relative}.device-toggle i:after{content:'';position:absolute;width:12px;height:12px;left:3px;top:3px;background:#aaa;border-radius:50%;transition:.2s}.device-toggle.on{color:white;border-color:#6b5124}.device-toggle.on i{background:var(--gold)}.device-toggle.on i:after{left:17px;background:#19130a}
  @media(max-width:700px){.saved-tools{grid-template-columns:1fr}.folder-movies{grid-template-columns:1fr}.nav-link{padding:10px}.language{padding:7px}}
</style>

<div class="shell">
  <header class="topbar">
    <button class="brand" on:click={() => tab = 'discover'} aria-label="Popcorn avaleht"><span>🍿</span><div><b>Popcorn</b><small>Osaühing X</small></div></button>
    <nav aria-label="Põhimenüü">
      <button class:active={tab === 'discover'} on:click={() => tab='discover'}>{ui.discover}</button>
      <a class="nav-link" href={`${base}/s_all`}>{ui.catalog}</a>
      <button class:active={tab === 'saved'} on:click={() => tab='saved'}>{ui.saved} <i>{local.length + family.events.length}</i></button>
      <button class:active={tab === 'folders'} on:click={() => tab='folders'}>{ui.folders}</button>
      <button class:active={tab === 'settings'} on:click={() => tab='settings'}>{ui.settings}</button>
    </nav>
    <div class="actions"><select class="language" value={$language} on:change={(e)=>changeLanguage(e.currentTarget.value)} aria-label="Portaali keel"><option value="et">ET</option><option value="en">EN</option></select><span class:online={ha.connected} class="status"><i></i>{ha.connected ? 'HA ühendatud' : 'Kohalik režiim'}</span><button class="icon" on:click={() => supportOpen=true} title="Abi ja tugi">?</button></div>
  </header>

  <main>
    {#if tab === 'discover'}
      <section class="hero">
        <div><span class="eyebrow">Popcorn · Osaühing X</span><h1>{ui.hero}</h1><p>{ui.lead}</p></div>
        <form class="search" on:submit|preventDefault={search}><span>⌕</span><input bind:value={query} placeholder={ui.search} aria-label="Otsing"><button>{ui.discover}</button></form>
      </section>
      <div class="section-head"><div><span class="eyebrow">TMDB</span><h2>{ui.popular}</h2></div><button class="ghost" on:click={loadMovies}>Värskenda ↻</button></div>
      {#if loading}<div class="loader">Laen filmimaagiat…</div>{:else if !visible.length}<div class="empty"><b>Midagi ei leitud</b><span>Proovi teist otsingusõna või kontrolli TMDB API võtit.</span></div>{:else}
        <div class="movie-grid">{#each visible as movie}<article class="movie-card"><a href={`${base}/${movie.media_type || 'movie'}/${movie.id}`}><img src={image(movie.poster_path)} alt={movie.title || movie.name} loading="lazy"><span class="score">★ {movie.vote_average?.toFixed(1) || '–'}</span></a><div><small>{movie.media_type === 'tv' ? 'SARI' : 'FILM'} · {(movie.release_date || movie.first_air_date || '').slice(0,4) || 'VARSTI'}</small><h3>{movie.title || movie.name}</h3><button class="save" on:click={() => openSave(movie)}>＋ Salvesta</button></div></article>{/each}</div>
      {/if}
    {:else if tab === 'saved'}
      <section class="page-title"><div><span class="eyebrow">Sinu vaatamisnimekiri</span><h1>Salvestatud</h1><p>Isiklikud valikud jäävad sellesse seadmesse. Pere valikud on kõigile Home Assistantis nähtavad.</p></div><button class="primary" on:click={() => openSave()}>＋ Lisa käsitsi</button></section>
      <div class="saved-tools"><label>Filtreeri<input bind:value={savedFilter} list="folder-filter" placeholder="Otsi nime või kausta järgi…"><datalist id="folder-filter">{#each family.folders as folder}<option value={folder.name}></option>{/each}</datalist></label><label>Sorteeri<select bind:value={savedSort}><option value="az">A–Z</option><option value="za">Z–A</option><option value="unreleased">Ilmumata</option><option value="old">Kuupäev: vanemad enne</option><option value="new">Kuupäev: uuemad enne</option></select></label></div>
      <FamilyCalendar items={[...local,...family.events]} bind:selectedMonth/><hr class="section-rule">
      <section class="library"><div class="section-head compact"><h2>Minu nimekiri <span>{filteredLocal.length}</span></h2><small>AINULT SELLES SEADMES</small></div>{#if filteredLocal.length}<div class="saved-grid">{#each filteredLocal as item}{@render Saved(item, false, null, () => remove(item, false))}{/each}</div>{:else}{@render Empty('Valitud filtriga isiklikke salvestusi ei leitud.')}{/if}</section>
      <section class="library"><div class="section-head compact"><h2>Pere nimekiri <span>{filteredFamily.length}</span></h2><small class:online={ha.connected}>HOME ASSISTANT</small></div>{#if filteredFamily.length}<div class="saved-grid">{#each filteredFamily as item}{@render Saved(item, true, family.folders.find(x => x.id === item.folderId), () => remove(item, true))}{/each}</div>{:else}{@render Empty('Valitud filtriga pere salvestusi ei leitud.')}{/if}</section>
    {:else if tab === 'folders'}
      <section class="page-title"><div><span class="eyebrow">Jagatud ruumid</span><h1>Pere kaustad</h1><p>Seo nimekiri inimestega, teavitustega ja filmiõhtu valgustusega.</p></div><button class="primary" on:click={() => {folderDraft=blankFolder();folderOpen=true}}>＋ Uus kaust</button></section>
      {#if family.folders.length}<div class="folder-grid">{#each family.folders as folder}<article class="folder" class:expanded={activeFolder===folder.id}><button class="folder-open" on:click={()=>activeFolder=activeFolder===folder.id?null:folder.id}><div class="folder-icon">⌂</div><div><small>{folder.room || 'RUUM MÄÄRAMATA'}</small><h2>{folder.name}</h2><p>{folder.members?.length || 0} liiget · {family.events.filter(x=>x.folderId===folder.id).length} salvestust</p></div><span>{activeFolder===folder.id?'−':'＋'}</span></button><div class="chips">{#each folder.members || [] as member}<span>{ha.people.find(x=>x.id===member)?.name || member}</span>{/each}</div>{#if activeFolder===folder.id}<div class="folder-movies">{#each family.events.filter(x=>x.folderId===folder.id) as item}{@render Saved(item,true,folder,()=>remove(item,true))}{:else}<p>Selles kaustas pole veel filme.</p>{/each}</div>{/if}<div class="device-list"><button class="lights" disabled={!folder.entities?.length||busy} on:click={()=>toggleEntities(folder)}>◐ Toggle kõik seadmed <small>{folder.entities?.length||0} seadet</small></button>{#each folder.entities||[] as entityId}{#if ha.controls.find(x=>x.id===entityId)}<button class:on={ha.controls.find(x=>x.id===entityId)?.state==='on'} class="device-toggle" disabled={busy} on:click={()=>toggleEntities(folder,[entityId])}><span>{ha.controls.find(x=>x.id===entityId)?.name}</span><i></i></button>{/if}{/each}</div><button class="ghost" on:click={() => {folderDraft=structuredClone(folder);folderOpen=true}}>Muuda seadeid</button></article>{/each}</div>{:else}{@render Empty('Loo esimene pere kaust ja seo see oma HA ruumiga.')}{/if}
    {:else}
      <section class="page-title"><div><span class="eyebrow">Popcorni seaded</span><h1>Teavitused</h1><p>Vali seadmed, kuhu lähevad kuupäevaga üldise pere nimekirja meeldetuletused. Kausta valikud kirjutavad need seaded üle.</p></div><span class:online={ha.connected} class="status"><i></i>{ha.connected ? 'Home Assistant ühendatud' : 'Käivita add-on Home Assistantis'}</span></section>
      <section class="settings-card"><span class="eyebrow">Vaikimisi saajad</span><h2>Home Assistanti notify-teenused</h2><p>Need leitakse automaatselt sinu Home Assistantist. Tavaliselt vastab <code>notify.mobile_app_…</code> ühele telefonile või kasutajale.</p><div class="checks">{#each ha.notifyServices as service}<label><input type="checkbox" checked={family.settings.notifyServices.includes(service)} on:change={()=>family.settings.notifyServices=toggle(family.settings.notifyServices,service)}><span>notify.{service}</span></label>{/each}{#if !ha.notifyServices.length}<p>Ühtegi notify teenust ei leitud. Home Assistanti paneeli püsiv teavitus luuakse kuupäevaga salvestusel siiski.</p>{/if}</div><button class="primary" disabled={busy} on:click={saveSettings}>Salvesta seaded</button></section>
    {/if}
  </main>
  <footer><span>🍿 Popcorn</span><p>Osaühing X toode · Loodud Eestis · Töötab lokaalselt sinu Home Assistantis</p><button on:click={() => supportOpen=true}>Tugi ja kontakt</button></footer>
</div>

{#if editorOpen}<div class="modal-backdrop" role="presentation" on:click={(e)=>e.currentTarget===e.target&&(editorOpen=false)}><section class="modal"><header><div><span class="eyebrow">Lisa nimekirja</span><h2>{draft.title || 'Uus salvestus'}</h2></div><button class="icon" on:click={()=>editorOpen=false}>×</button></header><div class="scope"><button class:active={scope==='local'} on:click={()=>scope='local'}><b>Minu nimekiri</b><small>Salvesta sellesse seadmesse</small></button><button class:active={scope==='family'} on:click={()=>scope='family'}><b>Pere nimekiri</b><small>Jaga Home Assistantis</small></button></div><form on:submit|preventDefault={save}><label>Pealkiri<input bind:value={draft.title} required placeholder="Filmi või sarja nimi"></label><label>Märkus<textarea bind:value={draft.note} rows="3" placeholder="Miks seda vaadata?"></textarea></label><label>Kuupäev <small>Kuupäev loob HA teavituse</small><input type="date" bind:value={draft.date} min={today}></label>{#if scope==='family'}<label>Kaust<select bind:value={draft.folderId}><option value="">Üldine pere nimekiri</option>{#each family.folders as f}<option value={f.id}>{f.name}</option>{/each}</select></label>{/if}<button class="primary wide" disabled={busy}>{busy?'Salvestan…':'Salvesta'}</button></form></section></div>{/if}

{#if folderOpen}<div class="modal-backdrop"><section class="modal large"><header><div><span class="eyebrow">Pere kaust</span><h2>{folderDraft.name || 'Uus kaust'}</h2></div><button class="icon" on:click={()=>folderOpen=false}>×</button></header><form on:submit|preventDefault={saveFolder}><div class="two"><label>Nimi<input bind:value={folderDraft.name} required placeholder="Nt Elutoa filmiõhtu"></label><label>Ruum<input bind:value={folderDraft.room} placeholder="Nt Elutuba"></label></div><fieldset><legend>Liikmed</legend><div class="checks">{#each ha.people as person}<label><input type="checkbox" checked={folderDraft.members.includes(person.id)} on:change={()=>folderDraft.members=toggle(folderDraft.members,person.id)}><span>{person.name}</span></label>{/each}{#if !ha.people.length}<p>Ühenda Home Assistant, et näha person.* üksusi.</p>{/if}</div></fieldset><fieldset><legend>Kes saab teavituse?</legend><div class="checks">{#each ha.notifyServices as service}<label><input type="checkbox" checked={folderDraft.notifyServices.includes(service)} on:change={()=>folderDraft.notifyServices=toggle(folderDraft.notifyServices,service)}><span>notify.{service}</span></label>{/each}{#if !ha.notifyServices.length}<p>Home Assistantis pole notify teenuseid saadaval.</p>{/if}</div></fieldset><fieldset><legend>Filmiõhtu tuled ja lülitid</legend><div class="checks scrollable">{#each ha.controls as entity}<label><input type="checkbox" checked={folderDraft.entities.includes(entity.id)} on:change={()=>folderDraft.entities=toggle(folderDraft.entities,entity.id)}><span>{entity.name}<small>{entity.id}</small></span></label>{/each}</div></fieldset><button class="primary wide" disabled={busy}>Salvesta kaust</button></form></section></div>{/if}

{#if supportOpen}<div class="modal-backdrop" on:click={(e)=>e.currentTarget===e.target&&(supportOpen=false)}><aside class="support"><button class="icon close" on:click={()=>supportOpen=false}>×</button><span class="support-mark"><img src={`${base}/logo.png`} alt="Osaühing X"></span><span class="eyebrow">Osaühing X</span><h2>Aitäh, et kasutad meie loodut.</h2><p>Popcorni arendatakse hoole ja kirega Eestis. Sinu toetus aitab meil ehitada veel paremaid kohalikke tööriistu Home Assistanti jaoks.</p><a class="primary wide" href="https://www.buymeacoffee.com/extaas" target="_blank" rel="noreferrer">☕ Toeta meie tegevust</a><a class="ghost wide" href="https://extaas.com/?popover=contact_popover" target="_blank" rel="noreferrer">Vajad abi? Võta ühendust ↗</a><small>Popcorn on Osaühing X toode.</small></aside></div>{/if}
{#if toast}<div class="toast">✓ {toast}</div>{/if}

{#snippet Empty(text)}<div class="empty"><b>🍿</b><span>{text}</span></div>{/snippet}
{#snippet Saved(item, familyItem, folder = null, onremove)}<article class="saved"><a class="saved-link" href={item.tmdbId?`${base}/${item.mediaType||'movie'}/${item.tmdbId}`:null} aria-label={`${item.title} info`}><div class="mini-poster">{#if item.image}<img src={item.image} alt="">{:else}<span>🍿</span>{/if}</div><div><small>{folder?.name || (familyItem?'PERE':'ISIKLIK')}</small><h3>{item.title}</h3>{#if item.note}<p>{item.note}</p>{/if}{#if item.date}<span class:soon={days(item.date)<=7} class="date">◷ {item.date} · {days(item.date)>=0?`${days(item.date)} päeva`:'möödunud'}</span>{/if}</div></a><button class="icon danger" on:click={onremove} title="Eemalda">×</button></article>{/snippet}
