<script>
  import { base } from '$app/paths';
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  let repo, env = '', message = '', error = '', status = {}, integrations = [];
  const id = page.url.searchParams.get('id');
  async function api(path, options = {}) { const response = await fetch(`${base}/api/${path}`, { headers: { 'Content-Type': 'application/json' }, ...options }); const data = await response.json(); if (!response.ok) throw new Error(data.message || data.error); return data; }
  async function load() { const state = await api('state'); repo = state.config.repositories.find((item) => item.fullName === id); status = state.status || {}; integrations = state.config.integrations || []; env = Object.entries(repo?.env || {}).map(([key, value]) => `${key}=${value}`).join('\n'); }
  function envObject() { return Object.fromEntries(env.split('\n').filter((line) => line.includes('=')).map((line) => [line.slice(0, line.indexOf('=')).trim(), line.slice(line.indexOf('=') + 1)])); }
  function integrationVersion(item) { const saved = integrations.find((entry) => entry.id === item.id); return { current: saved?.installedVersion || item.version || '—', available: saved?.availableVersion || item.version || '' }; }
  function applicationVersion(item) { const appStatus = status[item.id] || {}; return { current: appStatus.installedVersion || item.version || '—', available: appStatus.availableVersion || item.version || '' }; }
  async function save(rescan = false) { try { error = ''; await api('repositories', { method: 'PUT', body: JSON.stringify({ fullName: id, env: envObject(), rescan }) }); message = rescan ? 'Scan queued.' : 'Saved.'; await load(); } catch (reason) { error = reason.message; } }
  onMount(() => { load(); const timer = setInterval(load, 2000); return () => clearInterval(timer); });
</script>

{#if message}<p class="notice">{message}</p>{/if}{#if error}<p class="error">{error}</p>{/if}
{#if repo}
  <div class="summary"><span><b>{repo.integrations?.length || 0}</b> integrations</span><span><b>{repo.applications?.length || 0}</b> applications</span><span class="status" class:ready={repo.scanState === 'ready'} class:error-status={repo.scanState === 'error'}>{repo.scanState || 'waiting'}</span><button on:click={() => save(true)}>Rescan / Git pull</button></div>
  <h2>Integrations</h2>
  <table><thead><tr><th>Name</th><th>Domain</th><th>Version</th><th>Path</th></tr></thead><tbody>{#each repo.integrations || [] as item}{@const version = integrationVersion(item)}<tr on:click={() => location.href = `${base}/integration?id=${encodeURIComponent(item.id)}`}><td>{item.name}</td><td>{item.domain}</td><td><b>{version.current}</b>{#if version.available && version.available !== version.current}<span class="version-arrow">➜</span><b class="new-version">{version.available}</b>{/if}</td><td>{item.path}</td></tr>{:else}<tr><td colspan="4">None detected</td></tr>{/each}</tbody></table>
  <h2>Applications</h2>
  <table><thead><tr><th>Name</th><th>ID</th><th>Version</th><th>Port</th><th>Path</th></tr></thead><tbody>{#each repo.applications || [] as item}{@const version = applicationVersion(item)}<tr on:click={() => location.href = `${base}/application?id=${encodeURIComponent(item.id)}&repository=${encodeURIComponent(repo.fullName)}`}><td>{item.name}</td><td>{item.id}</td><td><b>{version.current}</b>{#if version.available && version.available !== version.current}<span class="version-arrow">➜</span><b class="new-version">{version.available}</b>{/if}</td><td>{item.port || '—'}</td><td>{item.path}</td></tr>{:else}<tr><td colspan="5">None detected. Add x_config.json to describe applications.</td></tr>{/each}</tbody></table>
  <h2>Repository environment</h2><textarea rows="10" bind:value={env} placeholder="NAME=value"></textarea><button class="primary" on:click={() => save(false)}>Save environment</button>
{/if}

<style>.version-arrow{margin:0 7px;color:#778392}.new-version{color:#58dfa9}.summary{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:25px}.summary span{padding:9px 12px;border:1px solid #2b333d;border-radius:6px;color:#9ba5b2}.summary b{color:#45dda3}.summary .status{border-color:#68591d;background:#28220e;color:#da3;text-transform:capitalize}.summary .status.ready{border-color:#276246;background:#123328;color:#65dfa9}.summary .status.error-status{border-color:#69343d;background:#32171c;color:#f29ca7}h2{font-size:14px;margin-top:28px}table{width:100%;border-collapse:collapse;border:1px solid #29313b;background:#0e1319}th,td{text-align:left;padding:10px 12px;border-bottom:1px solid #252c35}th{font-size:10px;color:#7f8996}tr{cursor:pointer}tbody tr:hover{background:#161c24}textarea{max-width:900px;display:block;margin-bottom:10px}.notice{color:#5ee0ae}.error{color:#f18c98}</style>
