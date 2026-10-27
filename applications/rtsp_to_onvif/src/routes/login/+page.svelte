<script>
 import {page} from '$app/stores';
 import {enhance} from '$app/forms';
 export let form;
 let busy=false;
 $: limited=form?.reason==='limited'||Number($page.url.searchParams.get('limited'))>0;
 $: invalid=form?.reason==='invalid'||$page.url.searchParams.get('invalid')==='1';
 $: next=form?.next||$page.url.searchParams.get('next')||'/';
 $: wait=Math.max(1,Math.min(60,Number(form?.retry_after||$page.url.searchParams.get('limited'))||60));
 $: error=limited?`Too many attempts. Please wait ${wait} seconds before trying again.`:invalid?'Incorrect password. Please try again.':form?.reason==='invalid_request'?'The sign-in request could not be read. Please try again.':'';
</script>
<svelte:head><title>Sign in · RTSP to ONVIF</title><meta name="robots" content="noindex,nofollow" /></svelte:head>
<main><section aria-labelledby="login-title">
 <div class="brand"><span class="mark" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="6" width="18" height="14" rx="3"/><circle cx="12" cy="13" r="3.5"/><path d="M8 6l1-3h6l1 3"/></svg></span><span>RTSP TO ONVIF</span></div>
 <p class="eyebrow">PRIVATE CAMERA MANAGEMENT</p><h1 id="login-title">Welcome back.</h1><p class="intro">Sign in to manage your cameras and relay settings.</p>
 <form method="POST" action={'/login?next='+encodeURIComponent(next)} aria-busy={busy} use:enhance={()=>{busy=true;return async({update})=>{try{await update();}finally{busy=false;}};}}>
  <input type="hidden" name="next" value={next}>
  <label for="management-password">Management password</label>
  <input id="management-password" name="password" type="password" autocomplete="current-password" required aria-invalid={error?'true':undefined} aria-describedby={error?'password-help login-error':'password-help'}>
  <p id="password-help" class="help">Use this installation's management password. Camera account passwords are separate.</p>
  {#if error}<p class="error" id="login-error" role="alert">{error}</p>{/if}
  <button disabled={busy}>{busy?'Signing in…':'Sign in'}<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14m-6-6l6 6-6 6"/></svg></button>
 </form>
 <p class="footnote">Your camera configuration stays on this installation.</p>
</section></main>
<style>
 :global(body){margin:0;background:#0e1419;color:#eff3f5;font:15px/1.55 Inter,system-ui,sans-serif;}main{box-sizing:border-box;min-height:100vh;min-height:100svh;display:grid;place-items:center;padding:28px 20px;}section{box-sizing:border-box;width:min(440px,100%);padding:34px;background:#192229;border:1px solid #596a77;border-radius:18px;box-shadow:0 24px 80px #0003;}.brand{display:flex;align-items:center;gap:11px;margin-bottom:36px;font-size:12px;font-weight:750;letter-spacing:.08em;}.mark{display:grid;place-items:center;width:34px;height:34px;border:1px solid #b69d6d;border-radius:10px;color:#efd8a7;font-size:22px;}.eyebrow{font-size:10px;font-weight:750;letter-spacing:.14em;color:#cebd9d;margin:0 0 10px;}h1{font-size:34px;line-height:1.15;letter-spacing:-.04em;margin:0 0 14px;}.intro{color:#c3cdd4;margin:0 0 28px;font-size:15px;}form{display:grid;gap:9px;}label{font-size:13px;font-weight:650;}input{box-sizing:border-box;min-height:48px;width:100%;padding:12px 13px;font:inherit;background:#0c141a;border:1px solid #8193a0;border-radius:8px;color:#fff;}input:focus-visible,button:focus-visible{outline:3px solid #add9fa;outline-offset:4px;}input[aria-invalid=true]{border-color:#efa2ac;}.help{font-size:12px;line-height:1.6;color:#bdc8d0;margin:2px 0 12px;}.error{border:1px solid #d68a96;border-radius:8px;padding:12px;background:#381e25;color:#ffe0e6;margin:0 0 9px;font-size:13px;line-height:1.6;}button{display:flex;align-items:center;justify-content:space-between;min-height:48px;padding:12px 16px;border:1px solid #edd5a4;border-radius:8px;background:#edd5a4;color:#192128;font:700 14px/1.5 system-ui;cursor:pointer;}button:disabled{opacity:.7;cursor:wait;}.footnote{margin:24px 0 0;font-size:11px;color:#b0bdc6;border-top:1px solid #52616b;padding-top:18px;}@media(max-width:480px){section{padding:28px 24px;}.brand{margin-bottom:30px;}h1{font-size:31px;}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto;}}
</style>
