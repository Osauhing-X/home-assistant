<script>
  import { base } from '$app/paths';
  import { onMount } from 'svelte';

  let events = [];
  let scope = '';
  let query = '';
  let error = '';

  async function load() {
    const response = await fetch(`${base}/api/audit?scope=${encodeURIComponent(scope)}&q=${encodeURIComponent(query)}`);
    events = (await response.json()).events;
  }

  async function cleanup() {
    if (!confirm('Delete all activity log entries?')) return;
    error = '';
    const response = await fetch(`${base}/api/audit`, { method: 'DELETE' });
    if (!response.ok) {
      const result = await response.json().catch(() => ({}));
      error = result.message || result.error || 'Could not clean up logs.';
      return;
    }
    await load();
  }

  onMount(load);
</script>

<div class="filters">
  <input bind:value={query} on:input={load} placeholder="Search activity…" />
  <select bind:value={scope} on:change={load}>
    <option value="">All sources</option>
    <option value="portal">Portal</option>
    <option value="repository">Repositories</option>
    <option value="integration">Integrations</option>
    <option value="application">Applications</option>
  </select>
  <button class="cleanup" on:click={cleanup}>Cleanup logs</button>
</div>
{#if error}<p class="error">{error}</p>{/if}
<div class="events">
  {#each events as event}
    <article><time>{new Date(event.timestamp).toLocaleString()}</time><span>{event.scope}</span><div><b>{event.subject}</b><p>{event.action}{event.details ? ` · ${event.details}` : ''}</p></div></article>
  {:else}<p class="empty">No matching activity yet.</p>{/each}
</div>

<style>
  .filters{display:grid;grid-template-columns:1fr 220px auto;gap:8px;margin-bottom:13px}.cleanup{white-space:nowrap;color:#ef9aa4;border-color:#57323a}.events{border:1px solid #29313b;border-radius:8px;background:#0d1218}.events article{display:grid;grid-template-columns:155px 90px 1fr;gap:12px;padding:11px 13px;border-bottom:1px solid #242c35}.events article:last-child{border-bottom:0}time,.events span{color:#7e8997;font-size:11px}.events span{text-transform:uppercase;color:#da3}.events b{color:#e6e9ed}.events p{margin:3px 0 0;color:#8994a2}.empty{padding:30px;text-align:center;color:#7f8997}.error{color:#f18d99}@media(max-width:700px){.filters{grid-template-columns:1fr}.events article{grid-template-columns:1fr}}
</style>
