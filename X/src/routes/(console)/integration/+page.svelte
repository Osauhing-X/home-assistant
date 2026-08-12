<script>
  import { base } from '$app/paths';
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  let item, message='', error='';
  const id=page.url.searchParams.get('id');
  async function api(path,options={}){const response=await fetch(`${base}/api/${path}`,{headers:{'Content-Type':'application/json'},...options});const data=await response.json();if(!response.ok)throw new Error(data.message||data.error);return data}
  async function load(){const state=await api('state');item=state.config.integrations.find(entry=>entry.id===id)}
  async function update(){try{await api('actions',{method:'POST',body:JSON.stringify({action:'update-integration',integrationId:id})});message='Install/update queued.'}catch(reason){error=reason.message}}
  onMount(load);
</script>

{#if item}<div class="facts"><article><small>Domain</small><b>{item.domain}</b></article><article><small>Installed version</small><b>{item.installedVersion||'Not installed'}</b></article><article><small>Available version</small><b>{item.version||'—'}</b></article><article><small>Update state</small><b>{item.installed&&item.version!==item.installedVersion?'Update available':'Current'}</b></article><article><small>Repository</small><b>{item.repository}</b></article><article><small>Path</small><b>{item.path}</b></article><article><small>Installed/updated</small><b>{item.installedAt?new Date(item.installedAt).toLocaleString():'—'}</b></article><article><small>Detected version</small><b>{item.availableVersion||item.version||'—'}</b></article></div><section class="info"><h2>Managed source</h2><p>The installed source is archived under X Platform persistent storage. Removing the repository does not remove this integration. New versions are staged in <code>new_version</code>, allowing Home Assistant to display its update entity until you approve installation.</p></section><button class="primary" on:click={update}>{item.installed?'Install available version':'Install integration'}</button>{/if}{#if message}<p class="ok">{message}</p>{/if}{#if error}<p class="bad">{error}</p>{/if}

<style>.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px}.facts article{display:grid;gap:6px;padding:14px;border:1px solid #29313b;background:#0e1319;border-radius:7px}.facts small{color:#838e9b}.facts b{color:#e7ebef;overflow-wrap:anywhere}.info{margin:18px 0;max-width:850px}.info p{color:#939eab;line-height:1.6}.info code,.ok{color:#da3}.bad{color:#f18d99}</style>
