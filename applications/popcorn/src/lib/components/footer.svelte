<script>
  import { base } from '$app/paths';
  import { t } from '$lib/assets/translations';
  import { helpOpen } from '$lib/assets/help';
</script>
<svelte:window on:keydown={(event) => { if (event.key === 'Escape') $helpOpen = false; }}/>
<footer><span>🍿 Popcorn</span><p>{$t("An Osaühing X product · Made in Estonia · Runs locally in your Home Assistant")}</p><button on:click={() => $helpOpen=true}>{$t("Support and contact")}</button></footer>
{#if $helpOpen}<div class="modal-backdrop" on:click={(e)=>e.currentTarget===e.target&&($helpOpen=false)}><aside class="support" role="dialog" aria-modal="true" aria-label={$t("Help and support")} tabindex="-1"><button class="icon close" on:click={()=>$helpOpen=false}>×</button><span class="support-mark"><img src={`${base}/logo.png`} alt="Osaühing X"></span><span class="eyebrow">Osaühing X</span><h2>{$t("Thank you for using what we build.")}</h2><p>{$t("Popcorn is built with care and passion in Estonia. Your support helps us build better local tools for Home Assistant.")}</p><a class="primary wide" href="https://www.buymeacoffee.com/extaas" target="_blank" rel="noreferrer">{$t("☕ Support our work")}</a><a class="ghost wide" href="https://extaas.com/?popover=contact_popover" target="_blank" rel="noreferrer">{$t("Need help? Contact us ↗")}</a><small>{$t("Popcorn is an Osaühing X product.")}</small></aside></div>{/if}

