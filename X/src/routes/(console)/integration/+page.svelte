<script>
  import { base } from '$app/paths';
  import { page } from '$app/state';
  import { onMount } from 'svelte';

  let item, message = '', error = '', docs = { available: false, content: '' }, logs = [], tab = 'overview';
  const id = page.url.searchParams.get('id');

  async function api(path, options = {}) {
    const response = await fetch(`${base}/api/${path}`, { cache: 'no-store', headers: { 'Content-Type': 'application/json' }, ...options });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || data.error);
    return data;
  }

  async function load() {
    const state = await api('state');
    item = state.config.integrations.find((entry) => entry.id === id);
    docs = await api(`docs?type=integration&id=${encodeURIComponent(id)}`).catch(() => ({ available: false, content: '' }));
    logs = (await api('logs?id=x-installer').catch(() => ({ lines: [] }))).lines.filter((line) => !item || line.includes(item.name) || line.includes(item.domain));
  }

  function asset(path) {
    return path && item?.repository ? `${base}/api/assets?repository=${encodeURIComponent(item.repository)}&path=${encodeURIComponent(path)}` : '';
  }

  async function action(type) {
    try {
      error = '';
      await api('actions', { method: 'POST', body: JSON.stringify({ action: type, integrationId: id }) });
      message = type === 'delete-integration' ? 'Delete queued.' : 'Download/install queued.';
      setTimeout(load, 1200);
    } catch (reason) { error = reason.message; }
  }

  onMount(() => { load(); const timer = setInterval(load, 2500); return () => clearInterval(timer); });
</script>

{#if item}
  {#if asset(item.background)}
    <section class="visual" style:background-image={`linear-gradient(90deg,#090c12f2,#090c1266),url('${asset(item.background)}')`}>
      {#if asset(item.logo || item.icon)}<img src={asset(item.logo || item.icon)} alt="" />{/if}
      <div><small>INTEGRATION</small><h2>{item.name}</h2><p>{item.description || item.repository}</p></div>
    </section>
  {:else}
    <section class="identity"><h2>{item.name}</h2><p>{item.description || item.repository}</p></section>
  {/if}
  <nav class="tabs"><button class:active={tab === 'overview'} on:click={() => tab = 'overview'}>Overview</button><button class:active={tab === 'logs'} on:click={() => tab = 'logs'}>Logs</button>{#if docs.available}<button class:active={tab === 'docs'} on:click={() => tab = 'docs'}>Docs</button>{/if}</nav>
  <section class="panel">
    {#if tab === 'overview'}
      <div class="facts"><article><small>Domain</small><b>{item.domain}</b></article><article><small>Version</small><b>{item.installedVersion || 'Not installed'}{#if item.stagedVersion && item.stagedVersion !== item.installedVersion}<span>➜</span><em>{item.stagedVersion}</em>{/if}</b></article><article><small>Update state</small><b>{item.installed && item.stagedVersion && item.stagedVersion !== item.installedVersion ? 'Update available' : 'Current'}</b></article><article><small>Repository</small><b>{item.repository}</b></article><article><small>Path</small><b>{item.path}</b></article><article><small>Installed/updated</small><b>{item.installedAt ? new Date(item.installedAt).toLocaleString() : '—'}</b></article></div>
      <section class="info"><h2>Managed source</h2><p>The installed source is archived under X Platform persistent storage. Removing the repository does not remove this integration.</p></section>
      <div class="overview-action">{#if item.installed}<button class="danger" on:click={() => confirm(`Delete ${item.name} from Home Assistant files?`) && action('delete-integration')}>Delete integration</button>{:else}<button class="primary" on:click={() => action('update-integration')}>Download integration</button>{/if}</div>
    {:else if tab === 'logs'}
      <div class="log-head"><h2>Activity</h2><button on:click={load}>Refresh</button></div><pre>{logs.join('\n') || 'No matching integration entries yet.'}</pre>
    {:else if tab === 'docs'}<pre class="docs">{docs.content}</pre>{/if}
  </section>
{/if}
{#if message}<p class="ok">{message}</p>{/if}{#if error}<p class="bad">{error}</p>{/if}

<style>
  .visual{min-height:190px;margin-bottom:14px;padding:25px;display:flex;align-items:end;gap:18px;border:1px solid #29313b;border-radius:12px;background:#10151c center/cover}.visual img{width:84px;height:84px;object-fit:contain;padding:8px;border-radius:17px;background:#090c12d9}.visual h2{font-size:28px;margin:4px 0}.visual p{margin:0}.visual small{color:#da3;font-weight:800;letter-spacing:.14em}.identity{margin:0 0 28px}.identity h2{font-size:28px;margin:0 0 5px}.identity p{margin:0;color:#aab3bf}
  .controls{display:flex;gap:8px;margin-bottom:12px}.danger{border:1px solid #a43a49;background:#6f202b;color:#fff}.tabs{display:flex;overflow:auto;border:1px solid #29313b;border-bottom:0;border-radius:8px 8px 0 0;background:#0d1218}.tabs button{border:0;border-radius:0;background:transparent;color:#8995a3;padding:11px 15px;white-space:nowrap}.tabs button.active{color:#da3;box-shadow:inset 0 -2px #da3}.panel{min-height:260px;padding:18px;border:1px solid #29313b;border-radius:0 0 8px 8px;background:#0b1016}.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px}.facts article{display:grid;gap:6px;padding:14px;border:1px solid #29313b;background:#0e1319;border-radius:7px}.facts small{color:#838e9b}.facts b{color:#e7ebef;overflow-wrap:anywhere}.facts span{margin:0 7px;color:#778392}.facts em{color:#58dfa9;font-style:normal}.info{margin-top:18px;max-width:850px}.info p{color:#939eab;line-height:1.6}.log-head{display:flex;align-items:center;justify-content:space-between}.panel pre{max-height:520px;margin:0;padding:14px;overflow:auto;white-space:pre-wrap;border:1px solid #222a33;border-radius:7px;background:#06090d;color:#da3}.panel pre.docs{color:#c8d0da;line-height:1.55}.ok{color:#da3}.bad{color:#f18d99}
  .overview-action{margin-top:24px;padding-top:18px;border-top:1px solid #29313b}
  @media(max-width:700px){.visual{align-items:start;flex-direction:column}}
</style>
