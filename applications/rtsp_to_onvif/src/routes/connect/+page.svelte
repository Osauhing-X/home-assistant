<script>
 import {onMount} from 'svelte';
 export let data;
 let connection=data.connection,error=data.error,busy=false;
 async function act(action){
  if(busy)return;busy=true;error='';
  try{const response=await fetch('/api/connect',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({action})});if(response.status===401){window.location.assign('/login?next=%2Fconnect');return;}const result=await response.json();if(!response.ok)throw Error(result.error||'The account service could not be reached.');connection=result;}
  catch(failure){error=failure.message||'The account service could not be reached.';}finally{busy=false;}
 }
 onMount(()=>{const timer=setInterval(()=>{if(connection?.status==='awaiting_confirmation'&&!error)void act('poll');},5000);return()=>clearInterval(timer);});
</script>
<svelte:head><title>Extaas Connect · RTSP to ONVIF</title><meta name="robots" content="noindex,nofollow" /></svelte:head>
<main>
 <nav aria-label="Camera relay"><a href="/">← Cameras</a><span>RTSP to ONVIF</span></nav>
 <header><p class="eyebrow">EXTAAS CONNECT</p><h1>Your relay. Your account.</h1><p class="intro">Connect this installation to your OUX account. Review and confirm the connection in Iseteenindus.</p></header>
 {#if error}<div class="error" role="alert">{error}</div>{/if}
 <section aria-labelledby="connection-title" aria-busy={busy}>
  <div class="section-head"><div><p class="eyebrow">ACCOUNT CONNECTION</p><h2 id="connection-title">{connection?.status==='connected'?'Connected account':connection?.status==='awaiting_confirmation'?'Confirm your connection':'Connect this installation'}</h2></div><span class="badge">{connection?.status==='connected'?'Connected':connection?.status==='awaiting_confirmation'?'Waiting for you':'Not connected'}</span></div>
  {#if connection?.status==='connected'}
   <p class="account">{connection.account_email}</p><p>This is the account to use when managing this installation in Iseteenindus.</p>
   <dl><div><dt>Installation ID</dt><dd>{connection.installation_id}</dd></div></dl>
   <div class="actions"><a class="primary" href={connection.manage_url} target="_blank" rel="noopener noreferrer">Manage in Iseteenindus ↗</a><button disabled={busy} on:click={()=>act('refresh')}>{busy?'Checking…':'Check connection'}</button></div>
  {:else if connection?.status==='awaiting_confirmation'}
   <ol><li>Open Iseteenindus and sign in to the account you want to connect.</li><li>Compare this code and approve the request you started.</li></ol>
   <div class="code"><span>Confirmation code</span><strong>{connection.user_code}</strong></div>
   <p class="waiting" role="status">Waiting for confirmation. This page checks automatically every five seconds.</p>
   <div class="actions"><a class="primary" href={connection.verification_uri} target="_blank" rel="noopener noreferrer">Open Iseteenindus ↗</a><button disabled={busy} on:click={()=>act('poll')}>Check now</button></div>
  {:else if connection?.enabled}
   <p>No licence key or token to copy. Start here, then approve the request in your account.</p><button class="primary" disabled={busy} on:click={()=>act('begin')}>{busy?'Starting connection…':'Connect with Extaas Connect'}</button>
   {#if connection.reason}<p role="status">{connection.reason}</p>{/if}
  {:else if !error}
   <p>Account linking is not enabled on this installation yet. It becomes available when the service is activated for this release.</p>
  {/if}
 </section>
 <aside aria-labelledby="access-title"><h2 id="access-title">Account connection and service access</h2><p>Connecting identifies your account and this installation. It does not confirm a paid service period. Paid access and the standalone addon rollout are still being prepared; the current camera configuration is preserved.</p></aside>
</main>
<style>
 :global(body){margin:0;background:#101519;color:#e9edf0;font-family:Inter,system-ui,sans-serif;}main{box-sizing:border-box;width:min(100%,1100px);margin:0 auto;padding:28px 28px 64px;}nav{display:flex;align-items:center;justify-content:space-between;gap:20px;border-bottom:1px solid #46515a;padding-bottom:24px;font-size:14px;color:#bdc8ce;}a{color:#f5dca9;text-underline-offset:4px;}header{padding:52px 0 32px;max-width:740px;}.eyebrow{font-size:11px;font-weight:700;letter-spacing:.14em;color:#c4b48f;margin:0 0 12px;}h1{font-size:clamp(32px,5vw,48px);letter-spacing:-.04em;line-height:1.12;margin:0 0 18px;}h2{font-size:20px;letter-spacing:-.02em;margin:0 0 12px;}p,li{font-size:15px;line-height:1.65;color:#c1cbd1;}.intro{font-size:17px;max-width:660px;}.section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;}.badge{white-space:nowrap;font-size:12px;color:#d9e3e9;border:1px solid #687985;border-radius:20px;padding:7px 11px;}section{padding:28px;background:#1b232a;border:1px solid #52616d;border-radius:16px;}.account{font-size:22px;font-weight:650;color:#f3f5f7;overflow-wrap:anywhere;}dl{margin:24px 0;}dt{font-size:12px;color:#c1cbd1;margin-bottom:8px;}dd{font-family:ui-monospace,monospace;margin:0;overflow-wrap:anywhere;font-size:13px;}.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px;align-items:center;}button,.primary{display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;min-height:46px;padding:11px 16px;border:1px solid #8193a1;border-radius:8px;background:transparent;color:#edf2f5;font:600 14px/1.4 system-ui;text-decoration:none;cursor:pointer;}button.primary,a.primary{background:#eed7a8;border-color:#eed7a8;color:#182027;}button:disabled{opacity:.65;cursor:wait;}button:focus-visible,a:focus-visible{outline:3px solid #a8d8ff;outline-offset:4px;}ol{padding-left:23px;}.code{display:flex;flex-wrap:wrap;align-items:center;gap:12px 24px;margin:26px 0;padding:18px;border:1px solid #697c89;border-radius:10px;color:#dce5ea;font-size:13px;}.code strong{font:700 26px/1.3 ui-monospace,monospace;letter-spacing:.08em;color:#fff;}.waiting{font-size:13px;}aside{margin-top:28px;padding:0 4px;max-width:800px;}aside h2{font-size:16px;}aside p{font-size:14px;}.error{background:#391e24;border:1px solid #dd8997;color:#ffe2e8;padding:16px;border-radius:10px;margin-bottom:20px;line-height:1.6;}@media(max-width:600px){main{padding:20px 18px 40px;}header{padding-top:36px;}section{padding:22px 18px;}.section-head{flex-direction:column;gap:4px;margin-bottom:18px;}.actions>*{width:100%;}nav{font-size:13px;}}
</style>
