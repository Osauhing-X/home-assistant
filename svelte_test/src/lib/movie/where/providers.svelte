<script>
  import { language } from '$lib/assets/language.js';
  import { page, navigating } from '$app/stores';

  let country;

  export let data, i18n = null;

  // reactive values
  $: ({ providers, title } = data);

  // fallback to "en" if not set
  $: lang = $language || "en";

  // current language name
  $: full = new Intl.DisplayNames([lang], { type: 'language' }).of(lang);

  // region names list
  $: list = providers.languages.map(code => ({
    code,
    name: new Intl.DisplayNames([lang], { type: 'region' }).of(code)
  }));

  // currently selected country + code
  $: country = list.find(c => c.name.toLowerCase() === full?.toLowerCase())?.name;
  $: what = list.find(c => c.name === country)?.code;

  function region_data(code) {
    let result = [];
    for (const value of Object.values(providers.providers)) {
      if (value.lang.includes(code)) {
        result.push(value);
      }
    }
    return result;
  }

  function get_url(provider) {
    return 'https://www.google.com/search?q=' + encodeURIComponent(provider + " " + title);
  }
</script>

<div>
  <label>{i18n?.region}
    <input type="search" list="region" placeholder="Region..." bind:value={country}>
    <datalist id="region">
      {#each list as item}
        <option value={item.name}></option>
      {/each}
    </datalist> 
  </label>
  <hr>

  {#if country}
    <div class="flex wrap gap">
      {#each region_data(what) as provider}
        <a href={get_url(provider.name)} target="_blank">{provider.name}</a>
      {/each}
    </div>
  {:else}
    <b>{i18n?.none}</b>
  {/if}
</div>

<style lang="scss">
flex {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  > a {
    border-radius: 5px;
    background: var(--transparent);
    padding: .2em .4em .2em .3em;
    gap: 7px;
  }
}
</style>
