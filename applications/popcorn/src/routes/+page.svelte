<script>
 import PortalFooter from "$lib/components/footer.svelte";
 import { helpOpen } from "$lib/assets/help";
 import { t, availableLanguages, isLocale, normalizeLocale } from '$lib/assets/translations';
 import {request} from '$lib/assets/request';
  import { base } from '$app/paths';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import FamilyCalendar from '$lib/pages/calender/family_calendar.svelte';
  import { filterSaved } from '$lib/assets/saved-list';
  import { language } from '$lib/config';

  let tab = 'discover', movies = [], loading = true, busy = false, family = { events: [], folders: [], settings: { notifyServices: [] } };
  let ha = { connected: false, people: [], controls: [], notifyServices: [] }, local = [], localFolders = [], query = '', scope = 'local', editorOpen = false, folderOpen = false, folderManagerOpen = false, folderViewerOpen = false;
  let draft = blank(), folderDraft = blankFolder(), folderScope = 'family', toast = '', savedFilter = '', savedSort = 'new', selectedMonth = '', activeFolder = null;
  function image(path) { return path ? `https://image.tmdb.org/t/p/w500${path}` : ''; }
  const today = new Date().toISOString().slice(0, 10);
  const days = (date) => Math.ceil((new Date(`${date}T12:00:00`) - new Date()) / 86400000);
  function blank(movie = {}) { return { tmdbId: movie.id || null, mediaType: movie.media_type || 'movie', title: movie.title || movie.name || '', image: image(movie.poster_path), reminder: false, date: '', note: '', folderId: '' }; }
  function blankFolder() { return { name: '', room: '', members: [], notifyServices: [], entities: [] }; }
  function flash(value) { toast = value; setTimeout(() => toast = '', 2600); }

  function createId() {
    if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
    return `popcorn-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }

  onMount(async () => {
    try { local = JSON.parse(localStorage.getItem('popcorn:personal') || '[]'); } catch { local = []; }
    try { localFolders = JSON.parse(localStorage.getItem('popcorn:folders') || '[]'); } catch { localFolders = []; }
    const params=new URLSearchParams(location.search);tab=params.get('view')||tab;$language=isLocale($page?.params?.lang)?$page.params.lang:normalizeLocale(params.get('language')||localStorage.getItem('popcorn:language'));
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
    try { const r = await fetch(`${base}/@_movie/json?api=${encoded}&query=${encodeURIComponent(query)}&include_adult=false&language=${$language}&fetch=1&page=1`); movies = (await r.json()).data || []; } finally { loading = false; }
  }
  async function loadFamily() {
    try { const r = await fetch(`${base}/@_popcorn/family`); const data = await r.json(); if (!r.ok || !Array.isArray(data.store?.events) || !Array.isArray(data.store?.folders)) throw new Error('Invalid family response'); family = data.store; ha = data.ha; }
    catch { flash($t("Could not load family data")); }
  }
  function openSave(movie = {}) { draft = blank(movie); scope = 'local'; editorOpen = true; }
  async function save() {
    if (!draft.title.trim()) return; busy = true;
    try {
      if (scope === 'local') {
        const item = { ...draft, id: draft.id || createId(), createdAt: draft.createdAt || new Date().toISOString() };
        local = [item, ...local.filter((entry)=>entry.id!==item.id)]; localStorage.setItem('popcorn:personal', JSON.stringify(local));
      } else {
        const r = await fetch(`${base}/@_popcorn/family`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ action: 'save', item: draft }) });
        if (!r.ok) throw new Error('Save failed');
        const data = await r.json(); if (!Array.isArray(data.store?.events)) throw new Error('Invalid response'); family = data.store;
      }
      editorOpen = false; flash(scope === 'local' ? $t("Saved to your list") : $t("Saved to the family list"));
    } catch { flash($t("Could not save. Please try again.")); } finally { busy = false; }
  }
  async function remove(item, familyItem) {
    if (familyItem) { const r = await api({ action: 'remove', id: item.id }); family = r.store; }
    else { local = local.filter((x) => x.id !== item.id); localStorage.setItem('popcorn:personal', JSON.stringify(local)); }
    flash($t("Removed"));
  }
  async function api(payload) { const r = await fetch(`${base}/@_popcorn/family`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }); if (!r.ok) throw new Error('Request failed'); return r.json(); }
  async function saveFolder() { busy = true; try { if(folderScope==='local'){const folder={...folderDraft,id:folderDraft.id||createId()};localFolders=[folder,...localFolders.filter(x=>x.id!==folder.id)];localStorage.setItem('popcorn:folders',JSON.stringify(localFolders))}else{const r = await api({ action: 'folder', folder: folderDraft }); family = r.store} folderOpen = false; folderDraft = blankFolder(); flash($t("Folder saved")); } finally { busy = false; } }
  function editSaved(item,familyItem){draft={...item,reminder:Boolean(item.date)};scope=familyItem?'family':'local';editorOpen=true}
  function openFolder(folder,isLocal){activeFolder={...folder,isLocal};folderViewerOpen=true}
  function editFolder(folder,isLocal){folderManagerOpen=false;folderViewerOpen=false;folderDraft=structuredClone(folder);folderScope=isLocal?'local':'family';folderOpen=true}
  async function removeFolder(folder,isLocal){if(isLocal){localFolders=localFolders.filter(x=>x.id!==folder.id);local=local.map(x=>x.folderId===folder.id?{...x,folderId:''}:x);localStorage.setItem('popcorn:folders',JSON.stringify(localFolders));localStorage.setItem('popcorn:personal',JSON.stringify(local))}else{const r=await api({action:'removeFolder',id:folder.id});family=r.store}flash('Kaust eemaldatud')}
  async function saveSettings() { busy = true; try { const r = await api({ action: 'settings', settings: { ...family.settings, language: $language } }); family = r.store; flash($t("Notification settings saved")); } finally { busy = false; } }
  async function lightsOff(folder) { busy = true; try { await api({ action: 'lightsOff', id: folder.id }); flash($t('{name}: lights turned off',{name:folder.room||folder.name})); } catch { flash($t("Home Assistant did not respond")); } finally { busy = false; } }
  async function toggleEntities(folder,entities=folder.entities||[],isLocal=false) { busy=true;try{const data=await api(isLocal?{action:'toggleLocalEntities',entities}:{action:'toggleEntities',id:folder.id,entities});ha=data.ha;flash(entities.length===1?$t("Device toggled"):$t("Folder devices toggled"))}catch{flash($t("Home Assistant did not respond"))}finally{busy=false} }
  function changeLanguage(value){$language=value;localStorage.setItem('popcorn:language',value);localStorage.setItem('save:language',value);const parts=$page.url.pathname.slice(base.length).split('/').filter(Boolean);if(isLocale(parts[0]))parts[0]=value;else parts.unshift(value);goto(`${base}/${parts.join('/')}${$page.url.search}`,{replaceState:true,noScroll:true,keepFocus:true});loadMovies();}
  const uiText=request('portal');
  $: ui=$uiText;
  $: portalBase=`${base}/${$language}`;
  function toggle(list, value) { return list.includes(value) ? list.filter((x) => x !== value) : [...list, value]; }
  const sorted = filterSaved;
  $: visible = movies.filter((x) => x.poster_path && (x.title || x.name));
  $: filteredLocal=sorted(local,savedFilter,savedSort,selectedMonth,localFolders);$: filteredFamily=sorted(family.events,savedFilter,savedSort,selectedMonth,family.folders);
</script>

<svelte:head><title>Popcorn · Osaühing X</title><meta name="theme-color" content="#09090d"></svelte:head>
<style>
  .settings-card { max-width: 760px; margin: 28px auto; padding: 28px; border: 1px solid var(--line); border-radius: 18px; background: var(--panel); }
  .settings-card h2 { margin: 0; font-size: 24px; }
  .settings-card > p { color: var(--muted); line-height: 1.6; }
  .settings-card .checks { margin: 22px 0; }
  .reminder-toggle{display:flex!important;grid-template-columns:none!important;align-items:center;gap:9px}.reminder-toggle input{width:auto!important;margin:0}
  .settings-card code { color: var(--gold); }
  .manager-list{display:grid;gap:8px;margin-top:18px}.manager-list h3{margin:14px 0 2px}.manager-list>div{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 12px;background:#111116;border:1px solid var(--line);border-radius:10px}.manager-list>div span{display:flex;gap:6px}
  .nav-link{color:var(--muted);text-decoration:none;padding:10px 15px;border-radius:10px;font-weight:600;white-space:nowrap}.nav-link:hover{background:#202027;color:white}.language{background:#17171c;color:white;border:1px solid var(--line);border-radius:9px;padding:8px}
  .saved-tools{display:grid;grid-template-columns:minmax(0,1fr) minmax(190px,280px);gap:12px;margin:26px 0 14px}.saved-tools label{display:grid;gap:6px;color:var(--muted);font-size:11px}.saved-tools input,.saved-tools select{background:var(--panel);color:white;border:1px solid var(--line);padding:12px;border-radius:11px}.section-rule{margin:28px 0;border:0;border-top:1px solid var(--line)}
  .saved{grid-template-columns:minmax(0,1fr) auto}.saved-actions{display:flex;gap:5px}.saved-link{display:grid;grid-template-columns:60px minmax(0,1fr);align-items:center;gap:14px;text-decoration:none;color:inherit;min-width:0}.title-actions{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:9px}.inline-folders{margin:0 0 14px}.drive-folder{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;padding:13px;background:#17171d;border:1px solid var(--line);border-radius:13px}.drive-folder-main{display:grid;grid-template-columns:40px minmax(0,1fr);gap:10px;align-items:center;background:none;border:0;color:inherit;text-align:left;cursor:pointer}.drive-folder-main span{font-size:24px}.drive-folder-main b,.drive-folder-main small{display:block}.drive-folder-main small{color:var(--muted);margin-top:3px}.drive-folder .lights{padding:9px}.folder-details{padding:16px;background:#0d0d11;border:0 solid #24242c;border-width:1px 0}.folder-details hr{border:0;border-top:1px solid var(--line);margin:16px 0}.folder-details .chips,.folder-movies,.device-list{margin:0}.folder-viewer{overflow:hidden}.folder-viewer>.folder-details{margin:0 -26px;padding:18px 26px}.folder-viewer-actions{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:18px}.folder-viewer-actions .lights{margin:0}.folder-movies{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.device-list{display:grid;gap:7px}.device-toggle{display:flex;align-items:center;justify-content:space-between;border:1px solid var(--line);background:#101014;color:var(--muted);border-radius:9px;padding:9px 11px;cursor:pointer}.device-toggle i{width:32px;height:18px;background:#333;border-radius:20px;position:relative}.device-toggle i:after{content:'';position:absolute;width:12px;height:12px;left:3px;top:3px;background:#aaa;border-radius:50%;transition:.2s}.device-toggle.on{color:white;border-color:#6b5124}.device-toggle.on i{background:var(--gold)}.device-toggle.on i:after{left:17px;background:#19130a}
  @media(max-width:700px){.saved-tools{grid-template-columns:1fr}.folder-movies{grid-template-columns:1fr}.nav-link{padding:10px}.language{padding:7px}}
</style>

<div class="shell">
  <header class="topbar">
    <button class="brand" on:click={() => tab = 'discover'} aria-label={$t("Popcorn home")}><span>🍿</span><div><b>Popcorn</b><small>Osaühing X</small></div></button>
    <nav aria-label={$t("Main navigation")}>
      <button class:active={tab === 'discover'} on:click={() => tab='discover'}>{ui.discover}</button>
      <a class="nav-link" href={`${portalBase}/s_all`}>{ui.catalog}</a>
      <button class:active={tab === 'saved'} on:click={() => tab='saved'}>{ui.saved} <i>{local.length + family.events.length}</i></button>
      <button class:active={tab === 'settings'} on:click={() => tab='settings'}>{ui.settings}</button>
    </nav>
    <div class="actions"><select class="language" value={$language} on:change={(e)=>changeLanguage(e.currentTarget.value)} aria-label={$t("Portal language")}>{#each availableLanguages as locale}<option value={locale.code}>{locale.code.toUpperCase()}</option>{/each}</select><button class="icon" on:click={() => $helpOpen=true} title={$t("Help and support")}>?</button></div>
  </header>

  <main>
    {#if tab === 'discover'}
      <section class="hero">
        <div><span class="eyebrow">Popcorn · Osaühing X</span><h1>{ui.hero}</h1><p>{ui.lead}</p></div>
        <form class="search" on:submit|preventDefault={search}><span>⌕</span><input bind:value={query} placeholder={ui.search} aria-label={$t("Search")}><button>{ui.discover}</button></form>
      </section>
      <div class="section-head"><div><span class="eyebrow">TMDB</span><h2>{ui.popular}</h2></div><button class="ghost" on:click={loadMovies}>{$t("Refresh ↻")}</button></div>
      {#if loading}<div class="loader">{$t("Loading movie magic…")}</div>{:else if !visible.length}<div class="empty"><b>{$t("Nothing found")}</b><span>{$t("Try another search or check the TMDB API key.")}</span></div>{:else}
        <div class="movie-grid">{#each visible as movie}<article class="movie-card"><a href={`${portalBase}/${movie.media_type || 'movie'}/${movie.id}`}><img src={image(movie.poster_path)} alt={movie.title || movie.name} loading="lazy"><span class="score">★ {movie.vote_average?.toFixed(1) || '–'}</span></a><div><small>{movie.media_type === 'tv' ? $t("SERIES") : $t("MOVIE")} · {(movie.release_date || movie.first_air_date || '').slice(0,4) || 'VARSTI'}</small><h3>{movie.title || movie.name}</h3><button class="save" on:click={() => openSave(movie)}>{$t("＋ Save")}</button></div></article>{/each}</div>
      {/if}
    {:else if tab === 'saved'}
      <section class="page-title"><div><span class="eyebrow">{$t("Your watchlist")}</span><h1>{$t("Saved")}</h1><p>{$t("Personal picks stay on this device. Family picks are visible to everyone in Home Assistant.")}</p></div><div class="title-actions"><button class="ghost" on:click={()=>folderManagerOpen=true}>{$t("Manage folders")}</button><button class="primary" on:click={() => openSave()}>＋ {$t("Add manually")}</button></div></section>
      <hr class="section-rule"><FamilyCalendar items={[...local,...family.events]} bind:selectedMonth/><hr class="section-rule">
      <div class="saved-tools"><label>{$t("Filter")}<input bind:value={savedFilter} list="folder-filter" placeholder={$t("Search by name or folder…")}><datalist id="folder-filter">{#each [...localFolders,...family.folders] as folder}<option value={folder.name}></option>{/each}</datalist></label><label>{$t("Sort")}<select bind:value={savedSort}><option value="az">A–Z</option><option value="za">Z–A</option><option value="unreleased">{$t("Unreleased")}</option><option value="old">{$t("Date: old to new")}</option><option value="new">{$t("Date: new to old")}</option></select></label></div>
      <section class="library"><div class="section-head compact"><h2>{$t("My list")} <span>{filteredLocal.length}</span></h2><small>{$t("ONLY ON THIS DEVICE")}</small></div>{#if localFolders.length}<div class="folder-grid inline-folders">{#each localFolders as folder}{@render FolderCard(folder,true,filteredLocal.filter(x=>x.folderId===folder.id))}{/each}</div>{/if}{#if filteredLocal.filter(x=>!x.folderId).length}<div class="saved-grid">{#each filteredLocal.filter(x=>!x.folderId) as item}{@render Saved(item, false, null, () => remove(item, false))}{/each}</div>{:else if !localFolders.length}{@render Empty($t("No personal saves match the selected filters."))}{/if}</section>
      <section class="library"><div class="section-head compact"><h2>{$t("Family list")} <span>{filteredFamily.length}</span></h2><small class:online={ha.connected}>HOME ASSISTANT</small></div>{#if family.folders.length}<div class="folder-grid inline-folders">{#each family.folders as folder}{@render FolderCard(folder,false,filteredFamily.filter(x=>x.folderId===folder.id))}{/each}</div>{/if}{#if filteredFamily.filter(x=>!x.folderId).length}<div class="saved-grid">{#each filteredFamily.filter(x=>!x.folderId) as item}{@render Saved(item, true, null, () => remove(item, true))}{/each}</div>{:else if !family.folders.length}{@render Empty($t("No family saves match the selected filters."))}{/if}</section>
    {:else}
      <section class="page-title"><div><span class="eyebrow">{$t("Popcorn settings")}</span><h1>{$t("Notifications")}</h1><p>{$t("Choose where dated family-list reminders are sent. Folder preferences override these settings.")}</p></div><span class:online={ha.connected} class="status"><i></i>{ha.connected ? $t("Home Assistant connected") : $t("Run the add-on in Home Assistant")}</span></section>
      <section class="settings-card"><span class="eyebrow">{$t("Default recipients")}</span><h2>{$t("Home Assistant notification services")}</h2><p>{$t("These are discovered automatically in Home Assistant. Usually,")} <code>notify.mobile_app_…</code> {$t("represents one phone or user.")}</p><div class="checks">{#each ha.notifyServices as service}<label><input type="checkbox" checked={family.settings.notifyServices.includes(service)} on:change={()=>family.settings.notifyServices=toggle(family.settings.notifyServices,service)}><span>notify.{service}</span></label>{/each}{#if !ha.notifyServices.length}<p>{$t("No notification services found. Dated saves will still create a persistent notification in Home Assistant.")}</p>{/if}</div><button class="primary" disabled={busy} on:click={saveSettings}>{$t("Save settings")}</button></section>
    {/if}
  </main>
  <PortalFooter/>
</div>

{#if editorOpen}<div class="modal-backdrop" role="presentation" on:click={(e)=>e.currentTarget===e.target&&(editorOpen=false)}><section class="modal"><header><div><span class="eyebrow">{$t("Add to list")}</span><h2>{draft.title || $t("New save")}</h2></div><button class="icon" on:click={()=>editorOpen=false}>×</button></header><div class="scope"><button class:active={scope==='local'} on:click={()=>scope='local'}><b>{$t("My list")}</b><small>{$t("Save on this device")}</small></button><button class:active={scope==='family'} on:click={()=>scope='family'}><b>{$t("Family list")}</b><small>{$t("Share in Home Assistant")}</small></button></div><form on:submit|preventDefault={save}><label>{$t("Title")}<input bind:value={draft.title} required placeholder={$t("Movie or series name")}></label><label>{$t("Note")}<textarea bind:value={draft.note} rows="3" placeholder={$t("Why watch this?")}></textarea></label><label class="reminder-toggle"><input type="checkbox" bind:checked={draft.reminder} on:change={() => { if (!draft.reminder) draft.date = '' }}> {$t("Add a reminder")}</label>{#if draft.reminder}<label>{$t("Reminder date")} <small>{$t("Popcorn sends a Home Assistant notification when this date arrives.")}</small><input type="date" bind:value={draft.date} min={draft.id ? undefined : today} required></label>{/if}<label>{$t("Folder")}<select bind:value={draft.folderId}><option value="">{scope==='family'?$t("General family list"):$t("My general list")}</option>{#each (scope==='family'?family.folders:localFolders) as f}<option value={f.id}>{f.name}</option>{/each}</select></label><button class="primary wide" disabled={busy}>{busy?$t("Saving…"):$t("Save")}</button></form></section></div>{/if}

{#if folderOpen}<div class="modal-backdrop"><section class="modal large"><header><div><span class="eyebrow">{$t("Family folder")}</span><h2>{folderDraft.name || $t("New folder")}</h2></div><button class="icon" on:click={()=>folderOpen=false}>×</button></header><form on:submit|preventDefault={saveFolder}><div class="two"><label>{$t("Name")}<input bind:value={folderDraft.name} required placeholder={$t("e.g. Living room movie night")}></label><label>{$t("Room")}<input bind:value={folderDraft.room} placeholder={$t("e.g. Living room")}></label></div><fieldset><legend>{$t("Members")}</legend><div class="checks">{#each ha.people as person}<label><input type="checkbox" checked={folderDraft.members.includes(person.id)} on:change={()=>folderDraft.members=toggle(folderDraft.members,person.id)}><span>{person.name}</span></label>{/each}{#if !ha.people.length}<p>{$t("Connect Home Assistant to see person.* entities.")}</p>{/if}</div></fieldset><fieldset><legend>{$t("Who receives notifications?")}</legend><div class="checks">{#each ha.notifyServices as service}<label><input type="checkbox" checked={folderDraft.notifyServices.includes(service)} on:change={()=>folderDraft.notifyServices=toggle(folderDraft.notifyServices,service)}><span>notify.{service}</span></label>{/each}{#if !ha.notifyServices.length}<p>{$t("No notification services are available in Home Assistant.")}</p>{/if}</div></fieldset><fieldset><legend>{$t("Movie night lights and switches")}</legend><div class="checks scrollable">{#each ha.controls as entity}<label><input type="checkbox" checked={folderDraft.entities.includes(entity.id)} on:change={()=>folderDraft.entities=toggle(folderDraft.entities,entity.id)}><span>{entity.name}<small>{entity.id}</small></span></label>{/each}</div></fieldset><button class="primary wide" disabled={busy}>{$t("Save folder")}</button></form></section></div>{/if}


{#if folderManagerOpen}<div class="modal-backdrop"><section class="modal large"><header><div><span class="eyebrow">{$t("Organize your lists")}</span><h2>{$t("Manage folders")}</h2></div><button class="icon" on:click={()=>folderManagerOpen=false}>×</button></header><div class="scope"><button on:click={()=>{folderDraft=blankFolder();folderScope='local';folderOpen=true}}>{$t("＋ New local folder")}</button><button on:click={()=>{folderDraft=blankFolder();folderScope='family';folderOpen=true}}>{$t("＋ New family folder")}</button></div><div class="manager-list"><h3>{$t("My folders")}</h3>{#each localFolders as folder}<div><b>{folder.name}</b><span><button class="ghost" on:click={()=>editFolder(folder,true)}>{$t("Edit")}</button><button class="icon danger" on:click={()=>removeFolder(folder,true)}>×</button></span></div>{/each}<h3>{$t("Family folders")}</h3>{#each family.folders as folder}<div><b>{folder.name}</b><span><button class="ghost" on:click={()=>editFolder(folder,false)}>{$t("Edit")}</button><button class="icon danger" on:click={()=>removeFolder(folder,false)}>×</button></span></div>{/each}</div></section></div>{/if}

{#if folderViewerOpen&&activeFolder}<div class="modal-backdrop" on:click={(event)=>event.currentTarget===event.target&&(folderViewerOpen=false)}><section class="modal large folder-viewer"><header><div><span class="eyebrow">{activeFolder.isLocal?$t("MY FOLDER"):$t("FAMILY FOLDER")}</span><h2>{activeFolder.name}</h2></div><button class="icon" on:click={()=>folderViewerOpen=false}>×</button></header><div class="folder-details"><div class="chips">{#each activeFolder.members||[] as member}<span>{ha.people.find(x=>x.id===member)?.name||member}</span>{/each}</div><hr><div class="folder-movies">{#each (activeFolder.isLocal?filteredLocal:filteredFamily).filter(x=>x.folderId===activeFolder.id) as item}{@render Saved(item,!activeFolder.isLocal,activeFolder,()=>remove(item,!activeFolder.isLocal))}{:else}<p>{$t("No saves match the filters in this folder.")}</p>{/each}</div><hr><div class="device-list">{#each activeFolder.entities||[] as entityId}{#if ha.controls.find(x=>x.id===entityId)}<button class:on={ha.controls.find(x=>x.id===entityId)?.state==='on'} class="device-toggle" disabled={busy} on:click={()=>toggleEntities(activeFolder,[entityId],activeFolder.isLocal)}><span>{ha.controls.find(x=>x.id===entityId)?.name}</span><i></i></button>{/if}{/each}</div></div><div class="folder-viewer-actions"><button class="ghost" on:click={()=>editFolder(activeFolder,activeFolder.isLocal)}>{$t("Settings")}</button><button class="lights" disabled={!activeFolder.entities?.length||busy} on:click={()=>toggleEntities(activeFolder,activeFolder.entities,activeFolder.isLocal)}>{$t("◐ Toggle all")}</button></div></section></div>{/if}

{#if toast}<div class="toast">✓ {toast}</div>{/if}

{#snippet Empty(text)}<div class="empty"><b>🍿</b><span>{text}</span></div>{/snippet}
{#snippet FolderCard(folder,isLocal,entries)}<article class="drive-folder"><button class="drive-folder-main" on:click={()=>openFolder(folder,isLocal)}><span>📁</span><div><b>{folder.name}</b><small>{entries.length} {$t("saves")}{folder.room?` · ${folder.room}`:''}</small></div></button><button class="lights" disabled={!folder.entities?.length||busy} on:click={()=>toggleEntities(folder,folder.entities,isLocal)}>{$t("◐ Toggle all")}</button></article>{/snippet}
{#snippet Saved(item, familyItem, folder = null, onremove)}<article class="saved"><a class="saved-link" href={item.tmdbId?`${portalBase}/${item.mediaType||'movie'}/${item.tmdbId}`:null} aria-label={`${item.title} info`}><div class="mini-poster">{#if item.image}<img src={item.image} alt="">{:else}<span>🍿</span>{/if}</div><div><small>{folder?.name || (familyItem?$t("FAMILY"):$t("PERSONAL"))}</small><h3>{item.title}</h3>{#if item.note}<p>{item.note}</p>{/if}{#if item.date}<span class:soon={days(item.date)<=7} class="date">◷ {item.date} · {days(item.date)>=0?$t('{count} days',{count:days(item.date)}):$t("past")}</span>{/if}</div></a><div class="saved-actions"><button class="icon" on:click={()=>editSaved(item,familyItem)} title={$t("Edit")}>✎</button><button class="icon danger" on:click={onremove} title={$t("Remove")}>×</button></div></article>{/snippet}
