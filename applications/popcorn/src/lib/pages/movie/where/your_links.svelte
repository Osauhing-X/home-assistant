<script> 
  import { onMount } from "svelte";
  import { urls } from "$lib/pages/movie/scripts/themoviedb_store";
  import { page } from '$app/stores';
  import { fav, view } from "$lib/pages/movie/scripts/favorite";

  export let i18n = null
  export let data;

  let type = $page?.params?.what;

  export let loc = "link";  // LocalStorage key

  let edit = false;
  let deleteMode = false;
  $: selected = [];
  let response = {};

  onMount(() => {
    const stored = fav().get()
    if (Array.isArray(stored)) urls.set(stored.map(normalizeLink));
    else for(const item of $urls) fav().save(loc, item);

    const unsubscribe = urls.subscribe(value => {
      fav().replace(loc, value)
    });

    return unsubscribe;
  });

  function normalizeLink(item) {
    return typeof item === 'string' ? { name: '', url: item } : { name: item?.name || '', url: item?.url || '' };
  }

  function updateLink(index, key, value) {
    urls.update(currentUrls => {
      currentUrls[index] = { ...normalizeLink(currentUrls[index]), [key]: value };
      fav().replace(loc, currentUrls);
      return [...currentUrls];
    });
  }

  function handleBlur(index) {
    urls.update(currentUrls => {
      if (!normalizeLink(currentUrls[index]).url.trim()) {
        const removed = currentUrls.splice(index, 1);
        if (removed[0]) fav().remove(loc, removed[0]);
      }
      return currentUrls;
    });
  }

  function addUrl() {
    urls.update(currentUrls => [...currentUrls, { name: '', url: '' }]);
  }

  function handleDelete() {
    urls.update(currentUrls => {
      const toRemove = selected.map(i => currentUrls[i]);
      toRemove.forEach(domain => fav().remove(loc, domain));
      const filtered = currentUrls.filter((_, index) => !selected.includes(index));
      return filtered;
    });

    selected = [];
  }

  function delete_list(index) {
    if (selected.includes(index)) {
      selected = selected.filter(i => i !== index);
    } else {
      selected = [...selected, index];
    }
  }

  function encodeSymbols(str) {
    return encodeURIComponent(str).replace(/[!'()*]/g, c =>
      '%' + c.charCodeAt(0).toString(16).toUpperCase());
  }

  function replacePlaceholders(item) {
    return normalizeLink(item).url
      .replace("[name]", encodeSymbols(data))
      .replace("[type]", encodeSymbols(type));
  }

  function getDomainName(item) {
    const link = normalizeLink(item);
    if (link.name.trim()) return link.name.trim();
    try {
      const replacedUrl = replacePlaceholders(link);
      const hostname = new URL(replacedUrl.trim()).hostname;
      const parts = hostname.split('.');
      const domainName = parts.length > 1 ? parts[parts.length - 2] : parts[0];
      return domainName.charAt(0).toUpperCase() + domainName.slice(1);
    } catch {
      const formattedUrl = `https://${link.url.trim()}`;
      try {
        const replacedUrl = replacePlaceholders(formattedUrl);
        const hostname = new URL(replacedUrl.trim()).hostname;
        const parts = hostname.split('.');
        const domainName = parts.length > 1 ? parts[parts.length - 2] : parts[0];
        return domainName.charAt(0).toUpperCase() + domainName.slice(1);
      } catch {
        return link.url.trim();
      }
    }
  }

  function formatUrl(item) {
    const link = normalizeLink(item);
    try {
      const replacedUrl = replacePlaceholders(link);
      return new URL(replacedUrl.trim()).href;
    } catch {
      return `https://${replacePlaceholders(link)}`;
    }
  }
</script>

<section id="your_links">
  <header class="links-head"><div><span class="eyebrow">Isiklikud otseteed</span><h3>Otsi seda sisu oma lemmikkohtadest</h3><p>{i18n?.links_txt || 'Lisa otsingu- või voogedastuslingid. [name] asendatakse automaatselt filmi või sarja nimega.'}</p></div><button class="edit-links" on:click={() => { edit = !edit; if (!edit) selected = [] }}>{edit ? 'Valmis' : 'Muuda linke'}</button></header>
  <hr>
  <div aria-label="list" class={edit ? "grid gap" : "flex wrap gap"}>
    {#if edit}
      {#if Array.isArray($urls) && $urls.length > 0}
        {#each $urls as url, index}
          <div class="link-editor">
            <input checked={selected.includes(index)} type="checkbox"
              on:change={() => delete_list(index)} />
            <input class="link-name" value={normalizeLink(url).name} placeholder="Name (optional)" on:input={(event) => updateLink(index, 'name', event.currentTarget.value)} />
            <textarea
              on:keydown={(e) => { if (e.key === 'Enter') e.preventDefault(); }}
              placeholder={i18n?.textarea}
              title="https://example.com/search?q=[name]"
              rows="2"
              on:input={(event) => updateLink(index, 'url', event.currentTarget.value)}
              on:blur={() => handleBlur(index)}
            >{normalizeLink(url).url}</textarea>
          </div>
        {/each}
        <div class="link-actions">
          <button on:click={() => { edit = !edit; if (!edit) selected = [] }}>Back</button>
          {#if selected.length > 0}
            <button aria-label="Delete" on:click={handleDelete}>Delete</button>
          {:else}
            <button aria-label="New" on:click={addUrl}>Add new</button>
          {/if}
        </div>
      {:else}
        <p>No URLs available.</p>
      {/if}
    {:else}
      {#if Array.isArray($urls) && $urls.length > 0}
        {#each $urls as url}
          <a aria-label="domain" href={formatUrl(url)} target="_blank" class="flex">
            <img src="https://s2.googleusercontent.com/s2/favicons?domain={formatUrl(url)}" alt="favicon"/>
            {getDomainName(url)}
          </a>
        {/each}
      {:else}
        <p>No URLs available.</p>
      {/if}
      {#each response.url || [] as url}
        <a aria-label="domain" href={formatUrl(url)} target="_blank" class="flex">
          <img src="https://s2.googleusercontent.com/s2/favicons?domain={formatUrl(url)}" alt="favicon"/>
          {getDomainName(url)}
        </a>
      {/each}
    {/if}
      </div>
</section>

<style lang="scss">
  .wrap {
    flex-wrap: wrap; }

section#your_links {
  .links-head { display:flex;align-items:start;justify-content:space-between;gap:18px;margin-bottom:16px; }
  .links-head h3 { margin:2px 0 6px;font-size:20px; }
  .links-head p { margin:0;max-width:650px;color:var(--muted);line-height:1.55; }
  .edit-links { flex:0 0 auto;padding:9px 12px;border:1px solid var(--line);border-radius:9px;background:#202027;color:white;cursor:pointer;font-weight:700; }
  .link-editor { display:grid!important;grid-template-columns:auto 1fr;gap:8px;align-items:start; }
  .link-editor textarea { grid-column:2;width:100%; }
  .link-name { width:100%;min-width:0;background:#0d0d11;color:white;border:1px solid var(--line);border-radius:9px;padding:9px; }
  .link-actions { display:flex;flex-wrap:wrap;gap:8px; }
  > div {
    > * { height: fit-content; }

    > input {
      border: 1px solid transparent;
      border-radius: 5px;
      line-height: 16px;
    }
    > a {
      border-radius: 5px;
      background: var(--transparent);
      padding: .2em .4em .2em .3em;
      gap: 7px;
      
      > img {
        vertical-align: sub;
        --height: 16px;}
    }
  }
}
@media(max-width:600px){section#your_links .links-head{display:grid}section#your_links .edit-links{width:max-content}}
div[aria-label="list"] {
  column-gap: .3em;
  input {
    &:checked ~ textarea {
      color: red;
    }
  }
}
</style>
