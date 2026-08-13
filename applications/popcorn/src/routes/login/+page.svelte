<script>
  import { page } from '$app/stores';
  $: next = $page.url.searchParams.get('next') || '/';
  $: invalid = $page.url.searchParams.get('invalid') === '1';
</script>

<svelte:head><title>Popcorn login</title></svelte:head>
<main>
  <form method="POST" action="/login/session">
    <span>POPCORN</span>
    <h1>Enter password</h1>
    <p>This application is protected by its X Platform configuration.</p>
    <input type="hidden" name="next" value={next} />
    <label>Password<input name="password" type="password" autocomplete="current-password" autofocus required /></label>
    {#if invalid}<small>The password is incorrect. Please try again.</small>{/if}
    <button>Continue</button>
  </form>
</main>

<style>
  :global(body){margin:0;background:#09090d;color:#f5f3ee;font-family:system-ui,sans-serif}main{min-height:100vh;display:grid;place-items:center;padding:24px}form{width:min(390px,100%);display:grid;gap:16px;padding:30px;border:1px solid #29282f;border-radius:18px;background:#131318;box-shadow:0 28px 80px #0008}span{color:#f4b942;font-size:10px;font-weight:800;letter-spacing:.18em}h1{margin:0;font-size:30px}p{margin:0;color:#96939e;line-height:1.5}label{display:grid;gap:7px;font-size:12px;font-weight:700}input{width:100%;box-sizing:border-box;padding:13px;border:1px solid #34333b;border-radius:10px;background:#0d0d11;color:white;font:inherit}input:focus{outline:0;border-color:#f4b942}button{padding:13px;border:0;border-radius:10px;background:#f4b942;color:#1c1304;font-weight:800;cursor:pointer}small{color:#ff8585}
</style>
