<script>
  import { base } from '$app/paths';
  import { page } from '$app/state';
  import { onMount } from 'svelte';

  let app, status = {}, catalog, logs = [], docs = { available: false, content: '' }, configured = false, installedApps = [];
  let message = '', error = '', envText = '', tab = 'overview';
  const id = page.url.searchParams.get('id');
  const repository = page.url.searchParams.get('repository');

  async function api(path, options = {}) {
    const response = await fetch(`${base}/api/${path}`, { headers: { 'Content-Type': 'application/json' }, ...options });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || data.error);
    return data;
  }

  async function load() {
    const state = await api('state');
    catalog = state.catalog.find((item) => item.id === id);
    installedApps = state.config.apps;
    const configuredApp = state.config.apps.find((item) => item.id === id);
    const discoveredApp = state.config.repositories.find((item) => item.fullName === (repository || configuredApp?.repository))?.applications?.find((item) => item.id === id) || catalog;
    configured = Boolean(configuredApp);
    app = configuredApp ? { ...discoveredApp, ...configuredApp, envSchema: configuredApp.envSchema?.length ? configuredApp.envSchema : (discoveredApp?.envSchema || []) } : discoveredApp;
    status = state.status[id] || {};
    const configuredEnv = app?.env || {};
    const envNames = [...new Set([...(app?.envSchema || []).map((item) => item.name), ...Object.keys(configuredEnv)])];
    envText = envNames.map((key) => `${key}=${configuredEnv[key] || ''}`).join('\n');
    docs = await api(`docs?id=${encodeURIComponent(id)}&repository=${encodeURIComponent(app?.repository||repository||'')}`).catch(() => ({ available: false, content: '' }));
    if (configured || status.state || status.error) {
      logs = (await api(`logs?id=${encodeURIComponent(id)}`)).lines;
    }
  }

  async function action(type) {
    try {
      error = '';
      if (!configured && type === 'install') {
        app.env = parseEnv();
        await api('apps', { method: 'POST', body: JSON.stringify({ ...app, pluginPath: app.pluginPath || app.path }) });
      }
      else if (configured && !status.installed && type === 'install') {
        app.env = parseEnv();
        await api('apps', { method: 'PUT', body: JSON.stringify({ ...app, installPending: true }) });
      }
      else await api('actions', { method: 'POST', body: JSON.stringify({ action: type, appId: id }) });
      message = `${type} queued.`;
      await load();
      if (type === 'install' && !status.installed) {
        status = { ...status, state: 'installing' };
        setTimeout(load, 1500);
      }
    } catch (reason) { error = reason.message; }
  }

  function parseEnv() {
    return Object.fromEntries(envText.split('\n').map((line) => line.trim()).filter((line) => line && !line.startsWith('#') && line.includes('=')).map((line) => [line.slice(0, line.indexOf('=')).trim(), line.slice(line.indexOf('=') + 1)]));
  }

  async function save() {
    try {
      error = '';
      app.env = parseEnv();
      if (configured) await api('apps', { method: 'PUT', body: JSON.stringify({ ...app, saveOnly: !status.installed }) });
      else await api('apps', { method: 'POST', body: JSON.stringify({ ...app, pluginPath: app.pluginPath || app.path, configureOnly: true }) });
      message = status.installed ? 'Configuration saved and restart queued.' : 'Configuration saved.';
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

  function asset(path) {
    const source = app?.repository || repository;
    return path && source ? `${base}/api/assets?repository=${encodeURIComponent(source)}&path=${encodeURIComponent(path)}` : '';
  }

  onMount(load);
  $: url = app ? `http://${location.hostname}:${app.port}` : '';
  $: portConflict = app ? installedApps.find((item) => item.id !== app.id && Number(item.port) === Number(app.port)) : null;
  $: missingRequiredEnv = app ? (app.envSchema || []).filter((item) => item.required && !String(parseEnv()[item.name] || '').trim()) : [];
</script>

  {#if app}
    {#if app.background || app.icon}<section class="visual" style:background-image={asset(app.background) ? `linear-gradient(90deg,#090c12f2,#090c1266),url('${asset(app.background)}')` : ''}>{#if asset(app.icon)}<img src={asset(app.icon)} alt="" />{/if}<div><small>APPLICATION</small><h2>{app.name}</h2><p>{app.description || app.repository}</p></div></section>{/if}

    <div class="controls">
      {#if status.state === 'installing' || status.state === 'updating'}<button class="primary" disabled>{status.state === 'installing' ? 'Installing…' : 'Updating…'}</button>
      {:else if !status.installed}<button class="primary" disabled={Boolean(portConflict) || missingRequiredEnv.length > 0} on:click={() => action('install')}>{configured ? 'Retry install' : 'Install'}</button>
      {:else if status.state === 'running'}<a href={url} target="_blank"><button class="primary">Open</button></a><button on:click={() => action('stop')}>Stop</button><button on:click={() => action('restart')}>Restart</button><button class:update-ready={status.updateAvailable} on:click={() => action('reload-code')}>{status.updateAvailable ? 'Update' : 'Reload code'}</button>
      {:else if status.state === 'error'}<button class="primary" on:click={() => action('reload-code')}>Retry / reload code</button>
      {:else}<button class="primary" on:click={() => action('start')}>Start</button><button class:update-ready={status.updateAvailable} on:click={() => action('reload-code')}>{status.updateAvailable ? 'Update' : 'Reload code'}</button>{/if}
      {#if status.installed}<span class:running={status.state === 'running'}>{status.state || 'stopped'}</span>{/if}
    </div>

    <nav class="tabs"><button class:active={tab === 'overview'} on:click={() => tab = 'overview'}>Overview</button><button class:active={tab === 'config'} on:click={() => tab = 'config'}>Config</button><button class:active={tab === 'env'} on:click={() => tab = 'env'}>Environment variables</button><button class:active={tab === 'logs'} on:click={() => tab = 'logs'}>Logs</button>{#if docs.available}<button class:active={tab === 'docs'} on:click={() => tab = 'docs'}>Docs</button>{/if}</nav>
    <section class="panel">
      {#if tab === 'overview'}
        <div class="overview"><article><small>Status</small><b>{status.state || (configured ? 'configured' : 'not installed')}</b></article><article><small>Port</small><b>{app.port}</b></article><article><small>PID</small><b>{status.pid || '—'}</b></article><article><small>Repository</small><b>{app.repository}</b></article></div>
        {#if !status.installed}<div class="setup-note"><small>INSTALLATION SETUP</small><h2>Configure before installing</h2><p>Open the Config tab to review the values from <code>x_config.json</code>, add required ENV values, and save them before installation.</p></div>{/if}
        {#if status.error}<pre class="failure">{status.error}</pre>{/if}
      {:else if tab === 'config'}
        <div class="facts"><label>Application ID<input disabled value={app.id} /></label><label>Repository<input disabled value={app.repository || repository || ''} /></label><label>Path<input bind:value={app.pluginPath} placeholder={app.path || '.'} /></label><label>Port<input type="number" min="1024" max="65535" bind:value={app.port} /></label><label>Update policy<select bind:value={app.updatePolicy}><option value="manual">Manual approval</option><option value="automatic">Automatic update</option></select></label><label>Install command<input bind:value={app.install} /></label><label>Build command<input bind:value={app.build} /></label><label>Start command<input bind:value={app.start} /></label><label>Icon path<input bind:value={app.icon} /></label><label>Background path<input bind:value={app.background} /></label></div>
        {#if portConflict}<p class="conflict">Port {app.port} is already used by {portConflict.name}. Choose another port before installing.</p>{/if}
        <button class="primary save" on:click={save}>Save configuration{status.installed ? ' and restart' : ''}</button>
      {:else if tab === 'env'}
        <h2>Environment variables</h2><p class="env-format">Use one <code>NAME=value</code> per line. Quotes are optional and are preserved as part of the value, so prefer <code>SUVALINE=123</code>.</p>
        {#if app.envSchema?.length}<div class="env-schema">{#each app.envSchema as variable}<article><code>{variable.name}</code>{#if variable.required}<b>Required</b>{/if}<span>{variable.description || variable.label}</span>{#if variable.example}<small>Example: {variable.example}</small>{/if}</article>{/each}</div>{/if}
        <textarea rows="10" bind:value={envText} placeholder="NAME=value"></textarea>
        {#if missingRequiredEnv.length}<p class="conflict">Add the required value: {missingRequiredEnv.map((item) => item.name).join(', ')}.</p>{/if}
        <div class="save-row"><button class="primary" on:click={save}>Save environment variables{status.installed ? ' and restart' : ''}</button></div>
      {:else if tab === 'logs'}
        <div class="log-head"><h2>Terminal</h2><div><button on:click={load}>Refresh</button><button class="clean" on:click={cleanLogs}>Clean</button></div></div><pre class="console">{logs.join('\n') || 'No terminal entries yet.'}</pre>
      {:else if tab === 'docs'}<pre class="docs">{docs.content}</pre>{/if}
    </section>
  {/if}
  {#if message}<p class="ok">{message}</p>{/if}{#if error}<p class="bad">{error}</p>{/if}

<style>
  .visual{min-height:190px;margin-bottom:14px;padding:25px;display:flex;align-items:end;gap:18px;border:1px solid #29313b;border-radius:12px;background:#10151c center/cover}.visual img{width:84px;height:84px;object-fit:contain;padding:8px;border-radius:17px;background:#090c12d9}.visual h2{font-size:28px;margin:4px 0}.visual p{margin:0}.visual small{color:#da3;font-weight:800;letter-spacing:.14em}.controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:12px}.controls>span{margin-left:auto;padding:6px 9px;border-radius:99px;background:#27181c;color:#ef8d99;text-transform:uppercase;font-size:10px}.controls>span.running{background:#29230e;color:#da3}.controls .update-ready{background:#23845e;border-color:#35aa7c;color:#fff;font-weight:800}.tabs{display:flex;overflow:auto;border:1px solid #29313b;border-bottom:0;border-radius:8px 8px 0 0;background:#0d1218}.tabs button{border:0;border-radius:0;background:transparent;color:#8995a3;padding:11px 15px;white-space:nowrap}.tabs button.active{color:#da3;box-shadow:inset 0 -2px #da3}.panel{min-height:260px;border:1px solid #29313b;border-radius:0 0 8px 8px;padding:18px;background:#0b1016}.overview{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.overview article{display:grid;gap:6px;padding:14px;border:1px solid #29313b;border-radius:7px}.overview small{color:#7f8a98}.overview b{overflow-wrap:anywhere}.facts{display:grid;grid-template-columns:1fr 1fr;gap:11px;max-width:900px}.facts label{display:grid;gap:5px;color:#909ba8}.save{margin-top:13px}textarea{display:block;font-family:ui-monospace,monospace;max-width:900px}.save-row{display:block;margin-top:12px}.save-row button{display:inline-block}.log-head{display:flex;align-items:center;justify-content:space-between}.log-head>div{display:flex;gap:7px}.clean{color:#f09aa5;border-color:#58313a}.console,.docs,.failure{white-space:pre-wrap;background:#06090d;border:1px solid #222a33;border-radius:7px;padding:14px;max-height:520px;overflow:auto;color:#da3}.docs{color:#c8d0da;line-height:1.55}.failure{color:#f18d99}.ok{color:#da3}.bad{color:#f18d99}code{color:#da3}@media(max-width:700px){.visual{align-items:start;flex-direction:column}.overview,.facts{grid-template-columns:1fr}.controls>span{margin-left:0}}
  .conflict{padding:10px;border:1px solid #69343d;border-radius:6px;background:#32171c;color:#f2a0aa!important}.env-schema{display:grid;gap:7px;margin-bottom:14px}.env-schema article{display:grid;grid-template-columns:auto auto 1fr;align-items:center;gap:8px;padding:9px 11px;border:1px solid #29313b;border-radius:6px}.env-schema code{font-weight:800}.env-schema b{padding:2px 5px;border-radius:99px;background:#332b10;color:#da3;font-size:9px;text-transform:uppercase}.env-schema span{color:#9ba5b1}.env-schema small{grid-column:1/-1;color:#707b89}@media(max-width:700px){.env-schema article{grid-template-columns:1fr}.env-schema small{grid-column:auto}}
</style>
