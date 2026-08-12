<script>
  import { base } from '$app/paths';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  let state={config:{apps:[]},status:{}};
  onMount(async()=>{try{const response=await fetch(`${base}/api/state`);if(response.ok)state=await response.json()}catch{}});
</script>

<svelte:head><title>Open X Platform</title></svelte:head>
<main class="launcher"><section><div class="intro"><img class="logo" src={`${base}/logo.png`} alt="X Platform"/><p>OSAÜHING X</p><h1>Open X Platform</h1></div><div class="choices"><a href={`${base}/dashboard`}><img src={`${base}/logo.png`} alt=""/><span><b>Console</b><small>Dashboard, repositories, integrations and logs</small></span></a>{#each state.config.apps.filter(app=>state.status[app.id]?.installed&&app.gui!==false) as app}<a href={`http://${$page.url.hostname}:${app.port}`} target="_top"><span class="letter">{app.name.slice(0,1)}</span><span><b>{app.name}</b><small>{state.status[app.id]?.state||'stopped'} · port {app.port}</small></span></a>{/each}</div><details><summary>Help and more</summary><ul><li><a href="https://extaas.com/?popover=contact_popover" target="_blank" rel="noreferrer">Help & support</a></li><li><a href="https://buymeacoffee.com/extaas" target="_blank" rel="noreferrer">Support the project</a></li></ul></details></section></main>

<style>
  :global(*){box-sizing:border-box}:global(body){margin:0;background:#0a0d12;color:#e7e9ed;font:14px Inter,system-ui,sans-serif}:global(a){color:inherit;text-decoration:none}.launcher{min-height:100vh;display:grid;place-items:center;padding:24px}.launcher>section{width:min(520px,100%);padding:0;border:1px solid #2c3440;border-radius:14px;background:#0e1319;box-shadow:0 28px 90px #0007;overflow:hidden}.intro{padding:30px}.logo{width:58px;height:58px;object-fit:contain}.launcher p{color:#da3;font-size:10px;letter-spacing:.17em;font-weight:800;margin:16px 0 6px}.launcher h1{font-size:26px;margin:0 0 24px}.choices{display:grid;grid-template-columns:1fr;gap:0;margin:0;padding:0;text-align:left;border:solid #2c3440;border-width:1px 0}.choices a{display:flex;align-items:center;gap:14px;padding:16px 30px;background:#0a0d12;transition:.18s}.choices a+a{border-top:1px solid #252c36}.choices a:hover{background:#151a21}.choices img,.letter{width:44px;height:44px;object-fit:contain;border-radius:9px}.letter{display:grid;place-items:center;background:#da3;color:#191405;font-size:20px;font-weight:900}.choices span:last-child{display:grid;gap:4px}.choices small{color:#8994a2;line-height:1.4}.launcher details{margin:0}.launcher summary{cursor:pointer;padding:16px 30px;color:#929dab;list-style:none}.launcher summary::after{content:'+';float:right;color:#da3}.launcher details[open] summary::after{content:'−'}.launcher details ul{margin:0;padding:0 30px 18px 48px;color:#8994a2}.launcher details li+li{margin-top:8px}.launcher details a{text-decoration:underline;text-underline-offset:3px}.launcher details a:hover{color:#da3}
</style>


