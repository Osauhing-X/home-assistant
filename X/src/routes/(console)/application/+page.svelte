<script>
  import { base } from '$app/paths';
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import Markdown from '$lib/Markdown.svelte';

  let app, status = {}, catalog, logs = [], docs = { available: false, content: '' }, configured = false, installedApps = [];
  let message = '', error = '', envValues = {}, tab = 'overview', queuedAction = '';
  const id = page.url.searchParams.get('id');
  const repository = page.url.searchParams.get('repository');

  function mergeEnvSchema(configuredSchema = [], discoveredSchema = []) {
    const configuredByName = new Map(configuredSchema.map((item) => [item.name, item]));
    const names = new Set([...discoveredSchema, ...configuredSchema].map((item) => item.name));
    return [...names].map((name) => ({ ...(configuredByName.get(name) || {}), ...(discoveredSchema.find((item) => item.name === name) || {}) }));
  }

  async function api(path, options = {}) {
    const response = await fetch(`${base}/api/${path}`, { cache: 'no-store', headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' }, ...options });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || data.error);
    return data;
  }

  async function load({ preserveForm = false } = {}) {
    const state = await api('state');
    catalog = state.catalog.find((item) => item.id === id);
    installedApps = state.config.apps;
    const configuredApp = state.config.apps.find((item) => item.id === id);
    const discoveredApp = state.config.repositories.find((item) => item.fullName === (repository || configuredApp?.repository))?.applications?.find((item) => item.id === id) || catalog;
    configured = Boolean(configuredApp);
    const loadedApp = configuredApp ? { ...discoveredApp, ...configuredApp, envSchema: mergeEnvSchema(configuredApp.envSchema || [], discoveredApp?.envSchema || []) } : discoveredApp;
    if (!preserveForm || !app) {
      app = loadedApp;
      const configuredEnv = app?.env || {};
      envValues = Object.fromEntries((app?.envSchema || []).map((item) => [item.name, configuredEnv[item.name] || '']));
    }
    status = state.status[id] || {};
    docs = await api(`docs?id=${encodeURIComponent(id)}&repository=${encodeURIComponent(app?.repository||repository||'')}`).catch(() => ({ available: false, content: '' }));
    logs = (await api(`logs?id=${encodeURIComponent(id)}`)).lines;
  }

  async function action(type) {
    try {
      error = '';
      if (['install', 'start', 'restart', 'reload-code'].includes(type) && missingRequiredEnv.length) {
        tab = 'env';
        error = `Required environment ${missingRequiredEnv.length === 1 ? 'variable is' : 'variables are'} missing: ${missingRequiredEnv.map((item) => item.name).join(', ')}. Add ${missingRequiredEnv.length === 1 ? 'it' : 'them'} under Environment variables and save the configuration.`;
        return;
      }
      if (!configured && type === 'install') {
        app.env = parseEnv();
        await api('apps', { method: 'POST', body: JSON.stringify({ ...app, pluginPath: app.pluginPath || app.path }) });
      }
      else if (configured && !status.installed && type === 'install') {
        app.env = parseEnv();
        await api('apps', { method: 'PUT', body: JSON.stringify({ ...app, installPending: true }) });
      }
      else await api('actions', { method: 'POST', body: JSON.stringify({ action: type, appId: id }) });
      queuedAction = type;
      message = `${type} queued.`;
      if (['install', 'reload-code'].includes(type)) tab = 'logs';
      await load();
      if (type === 'install' && !status.installed) {
        status = { ...status, state: 'installing' };
        setTimeout(load, 1500);
      }
    } catch (reason) { error = reason.message; }
  }

  function parseEnv() {
    return Object.fromEntries((app?.envSchema || []).map((item) => [item.name, envValues[item.name] || '']).filter(([, value]) => String(value).length));
  }

  async function save() {
    try {
      error = '';
      app.env = parseEnv();
      if (configured) await api('apps', { method: 'PUT', body: JSON.stringify({ ...app, saveOnly: !status.installed }) });
      else await api('apps', { method: 'POST', body: JSON.stringify({ ...app, pluginPath: app.pluginPath || app.path, configureOnly: true }) });
      const restarting = status.installed && app.enabled !== false;
      queuedAction = restarting ? 'restart' : '';
      message = restarting ? 'Configuration saved and restart queued.' : 'Configuration saved.';
      await load();
    } catch (reason) { error = reason.message; }
  }

  async function cleanLogs() {
    if (!confirm(`Delete all ${app.name} terminal entries?`)) return;
    try {
      error = '';
      await api(`logs?id=${encodeURIComponent(id)}`, { method: 'DELETE' });
      logs = [];
      message = 'Terminal logs cleaned.';
    } catch (reason) { error = reason.message; }
  }

  async function removeApplication() {
    if (!confirm(`Delete ${app.name} and its installed files?`)) return;
    try {
      await api('actions', { method: 'POST', body: JSON.stringify({ action: 'delete-application', appId: id }) });
      location.href = `${base}/applications`;
    } catch (reason) { error = reason.message; }
  }

  function asset(path) {
    const source = app?.repository || repository;
    return path && source ? `${base}/api/assets?repository=${encodeURIComponent(source)}&path=${encodeURIComponent(path)}` : '';
  }

  async function refreshLive() {
    await load({ preserveForm: true });
    if (!queuedAction) return;
    const queue = await api('queue').catch(() => ({ active: null, pending: [] }));
    const commands = [queue.active, ...(queue.pending || [])].filter(Boolean);
    if (!commands.some((command) => command.appId === id && command.type === queuedAction)) {
      queuedAction = '';
      message = '';
    }
  }

  onMount(() => { refreshLive(); const timer = setInterval(refreshLive, 1500); return () => clearInterval(timer); });
  $: url = app ? `http://${location.hostname}:${app.port}` : '';
  $: portConflict = app ? installedApps.find((item) => item.id !== app.id && Number(item.port) === Number(app.port)) : null;
  $: missingRequiredEnv = app ? (app.envSchema || []).filter((item) => item.required && !String(parseEnv()[item.name] || '').trim()) : [];
</script>
<svelte:head><style>.console{display:flex!important;flex-direction:column-reverse}</style></svelte:head>

  {#if app}
    {#if asset(app.background)}
      <section class="visual" style:background-image={`linear-gradient(90deg,#090c12f2,#090c1266),url('${asset(app.background)}')`}>
        {#if asset(app.logo || app.icon)}<img src={asset(app.logo || app.icon)} alt="" />{/if}
        <div><small>APPLICATION</small><h2>{app.name}</h2><p>{app.description || app.repository}</p></div>
      </section>
    {:else}
      <section class="identity"><h2>{app.name}</h2><p>{app.description || app.repository}</p></section>
    {/if}

    <div class="controls">
      {#if status.state === 'installing' || status.state === 'updating'}<button class="primary" disabled>{status.state === 'installing' ? 'Installing…' : 'Updating…'}</button>
      {:else if !status.installed}<button class="primary" disabled={Boolean(portConflict)} on:click={() => action('install')}>{configured ? 'Retry install' : 'Install'}</button>
      {:else if status.state === 'running'}<a href={url} target="_blank"><button class="primary">Open</button></a><button on:click={() => action('stop')}>Stop</button><button on:click={() => action('restart')}>Restart</button><button class:update-ready={status.updateAvailable} on:click={() => action('reload-code')}>{status.updateAvailable ? 'Update' : 'Reload code'}</button>
      {:else if status.state === 'error'}<button class="primary" on:click={() => action('reload-code')}>Retry / reload code</button>
      {:else}<button class="primary" on:click={() => action('start')}>Start</button><button class:update-ready={status.updateAvailable} on:click={() => action('reload-code')}>{status.updateAvailable ? 'Update' : 'Reload code'}</button>{/if}
    </div>
    {#if error}<div class="action-error"><b>Action required</b><span>{error}</span>{#if missingRequiredEnv.length}<button on:click={() => tab = 'env'}>Open Environment variables</button>{/if}</div>{/if}

    <nav class="tabs"><button class:active={tab === 'overview'} on:click={() => tab = 'overview'}>Overview</button><button class:active={tab === 'config'} on:click={() => tab = 'config'}>Config</button>{#if app.envSchema?.length}<button class:active={tab === 'env'} on:click={() => tab = 'env'}>Environment variables</button>{/if}<button class:active={tab === 'logs'} on:click={() => tab = 'logs'}>Logs</button>{#if docs.available}<button class:active={tab === 'docs'} on:click={() => tab = 'docs'}>Docs</button>{/if}</nav>
    <section class="panel">
      {#if tab === 'overview'}
        <div class="overview"><article><small>Status</small><b class="status-value" class:error={status.state === 'error'} class:busy={status.state === 'installing' || status.state === 'updating'} class:running={status.state === 'running'}>{status.state || (configured ? 'configured' : 'not installed')}</b></article><article><small>Version</small><b>{status.installedVersion || app.version || '—'}{#if status.availableVersion && status.availableVersion !== (status.installedVersion || app.version)} <span class="version-arrow">➜</span> <em>{status.availableVersion}</em>{/if}</b></article><article><small>Port</small><b>{app.port}</b></article><article><small>PID</small><b>{status.pid || '—'}</b></article><article><small>Repository</small><b>{app.repository}</b></article></div>
        {#if !status.installed}<div class="setup-note"><small>INSTALLATION SETUP</small><h2>Configure before installing</h2><p>Open the Config tab to review X metadata and commands detected from <code>package.json</code>, add required ENV values, and save them before installation.</p></div>{/if}
        {#if status.error}<pre class="failure">{status.error}</pre>{/if}
        {#if configured}<div class="overview-action"><button class="delete-app" on:click={removeApplication}>Delete application</button></div>{/if}
      {:else if tab === 'config'}
        <div class="facts"><label>Application ID<input disabled value={app.id} /></label><label>Repository<input disabled value={app.repository || repository || ''} /></label><label>Path<input bind:value={app.pluginPath} placeholder={app.path || '.'} /></label><label>Port<input type="number" min="1024" max="65535" bind:value={app.port} /></label><label>Update policy<select bind:value={app.updatePolicy}><option value="manual">Manual approval</option><option value="automatic">Automatic update</option></select></label><label>Install command<input bind:value={app.install} /></label><label>Build command<input bind:value={app.build} /></label><label>Start command<input bind:value={app.start} /></label><label>Logo path<input bind:value={app.logo} /></label><label>Background path<input bind:value={app.background} /></label></div>
        {#if portConflict}<p class="conflict">Port {app.port} is already used by {portConflict.name}. Choose another port before installing.</p>{/if}
        <button class="primary save" on:click={save}>Save configuration{status.installed && app.enabled !== false ? ' and restart' : ''}</button>
      {:else if tab === 'env' && app.envSchema?.length}
        <h2>Environment variables</h2>
        <div class="env-schema">{#each app.envSchema as variable}<article><div class="env-meta"><code>{variable.name}</code>{#if variable.required}<b>Required</b>{/if}<span>{variable.description || variable.label}</span>{#if variable.example}<small>Example: {variable.example}</small>{/if}</div><textarea rows="2" bind:value={envValues[variable.name]} placeholder={variable.label || variable.name}></textarea></article>{/each}</div>
        {#if missingRequiredEnv.length}<p class="conflict">Add the required value: {missingRequiredEnv.map((item) => item.name).join(', ')}.</p>{/if}
        <div class="save-row"><button class="primary" on:click={save}>Save environment variables{status.installed && app.enabled !== false ? ' and restart' : ''}</button></div>
      {:else if tab === 'logs'}
        <div class="log-head"><h2>Terminal</h2><div><button on:click={() => load({ preserveForm: true })}>Refresh</button><button class="clean" on:click={cleanLogs}>Clean</button></div></div><pre class="console">{logs.join('\n') || (queuedAction ? 'Waiting for terminal output…' : 'No terminal entries yet.')}</pre>
      {:else if tab === 'docs'}<Markdown content={docs.content} />{/if}
    </section>
  {/if}
  {#if message}<p class="ok">{message}</p>{/if}

<style>
  .version-arrow{color:#778392}.overview em{color:#58dfa9;font-style:normal}
  .identity{margin:0 0 28px}.identity h2{font-size:28px;margin:0 0 5px}.identity p{margin:0;color:#aab3bf}
  .visual{min-height:190px;margin-bottom:14px;padding:25px;display:flex;align-items:end;gap:18px;border:1px solid #29313b;border-radius:12px;background:#10151c center/cover}.visual img{width:84px;height:84px;object-fit:contain;padding:8px;border-radius:17px;background:#090c12d9}.visual h2{font-size:28px;margin:4px 0}.visual p{margin:0}.visual small{color:#da3;font-weight:800;letter-spacing:.14em}.controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:12px}.controls>span{margin-left:auto;padding:6px 9px;border-radius:99px;background:#27181c;color:#ef8d99;text-transform:uppercase;font-size:10px}.controls>span.running{background:#29230e;color:#da3}.controls .update-ready{background:#23845e;border-color:#35aa7c;color:#fff;font-weight:800}.tabs{display:flex;overflow:auto;border:1px solid #29313b;border-bottom:0;border-radius:8px 8px 0 0;background:#0d1218}.tabs button{border:0;border-radius:0;background:transparent;color:#8995a3;padding:11px 15px;white-space:nowrap}.tabs button.active{color:#da3;box-shadow:inset 0 -2px #da3}.panel{min-height:260px;border:1px solid #29313b;border-radius:0 0 8px 8px;padding:18px;background:#0b1016}.overview{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.overview article{display:grid;gap:6px;padding:14px;border:1px solid #29313b;border-radius:7px}.overview small{color:#7f8a98}.overview b{overflow-wrap:anywhere}.setup-note{margin-top:18px}.facts{display:grid;grid-template-columns:1fr 1fr;gap:11px;max-width:900px}.facts label{display:grid;gap:5px;color:#909ba8}.save{margin-top:13px}textarea{display:block;font-family:ui-monospace,monospace;max-width:900px}.save-row{display:block;margin-top:12px}.save-row button{display:inline-block}.log-head{display:flex;align-items:center;justify-content:space-between}.log-head>div{display:flex;gap:7px}.clean{color:#f09aa5;border-color:#58313a}.console,.failure{white-space:pre-wrap;background:#06090d;border:1px solid #222a33;border-radius:7px;padding:14px;max-height:520px;overflow:auto;color:#da3}.failure{color:#f18d99}.ok{color:#da3}.bad{color:#f18d99}code{color:#da3}@media(max-width:700px){.visual{align-items:start;flex-direction:column}.overview,.facts{grid-template-columns:1fr}.controls>span{margin-left:0}}
  .conflict{padding:10px;border:1px solid #69343d;border-radius:6px;background:#32171c;color:#f2a0aa!important}.env-schema{display:grid;gap:9px;margin-bottom:14px}.env-schema article{display:grid;gap:9px;padding:11px;border:1px solid #29313b;border-radius:6px}.env-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.env-schema code{font-weight:800}.env-schema b{padding:2px 5px;border-radius:99px;background:#332b10;color:#da3;font-size:9px;text-transform:uppercase}.env-schema span{color:#9ba5b1}.env-schema small{width:100%;color:#707b89}.env-schema textarea{width:100%;max-width:none}
  .delete-app{margin-left:auto;background:#6f202b;border-color:#a43a49;color:#fff}.status-value{text-transform:capitalize}.status-value.error{color:#f18d99}.status-value.busy{color:#65b8ff}.status-value.running{color:#58dfa9}
  .overview-action{margin-top:24px;padding-top:18px;border-top:1px solid #29313b}.delete-app{margin-left:0}
  .action-error{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 12px;padding:12px 14px;border:1px solid #7a3741;border-radius:7px;background:#35171d;color:#f3a5ae}.action-error b{color:#fff}.action-error span{flex:1;min-width:240px}.action-error button{white-space:nowrap;border-color:#a64a57;background:#642631;color:#fff}
</style>
