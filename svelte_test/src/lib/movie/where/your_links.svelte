<script> 
  import { onMount } from "svelte";
  import { urls } from "$lib/movie/themoviedb_store";
  import { page } from '$app/stores';
  import { save, view } from "$lib/movie/discover_store.js";

  export let i18n = null
  export let data;

  let type = $page?.params?.what;

  export let loc = "link";  // LocalStorage key

  let edit = false;
  let deleteMode = false;
  $: selected = [];
  let response = {};

  onMount(() => {
    const stored = save(loc, "get");
    if (Array.isArray(stored)) urls.set(stored);
    else for(const item of $urls) save(loc, "save", item)

    const unsubscribe = urls.subscribe(value => {
      save(loc, "replace", value);
    });

    return unsubscribe;
  });

  function updateUrl(event, index) {
    const value = event.target.value.trim();
    urls.update(currentUrls => {
      currentUrls[index] = value;
      save(loc, "replace", currentUrls);
      return currentUrls;
    });
  }

  function handleBlur(index) {
    urls.update(currentUrls => {
      if (currentUrls[index].trim() === "") {
        const removed = currentUrls.splice(index, 1);
        if (removed[0]) save(loc, "remove", removed[0]);
      }
      return currentUrls;
    });
  }

  function addUrl() {
    if (confirm($i18n?.confirm)) {

      let domainInput = prompt($i18n?.prompt, "https://youtube.com/results?search_query=extaas")

      if (!domainInput) return;

      let domain = domainInput.toLowerCase();

      if (!domain.includes("extaas.com") && domain.includes("extaas")) {
        domain = domain.replace(/extaas/g, '[name]');
      }

      urls.update(currentUrls => {
        if (!currentUrls.includes(domain)) {
          currentUrls.push(domain);
          save(loc, 'save', domain); }

        else console.log('🟡', $i18n?.exists)
        
        return currentUrls;
      });
    }
  }

  function handleDelete() {
    urls.update(currentUrls => {
      const toRemove = selected.map(i => currentUrls[i]);
      toRemove.forEach(domain => save(loc, 'remove', domain));
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

  function replacePlaceholders(url) {
    return url
      .replace("[name]", encodeSymbols(data))
      .replace("[type]", encodeSymbols(type));
  }

  function getDomainName(url) {
    try {
      const replacedUrl = replacePlaceholders(url);
      const hostname = new URL(replacedUrl.trim()).hostname;
      const parts = hostname.split('.');
      const domainName = parts.length > 1 ? parts[parts.length - 2] : parts[0];
      return domainName.charAt(0).toUpperCase() + domainName.slice(1);
    } catch {
      const formattedUrl = `https://${url.trim()}`;
      try {
        const replacedUrl = replacePlaceholders(formattedUrl);
        const hostname = new URL(replacedUrl.trim()).hostname;
        const parts = hostname.split('.');
        const domainName = parts.length > 1 ? parts[parts.length - 2] : parts[0];
        return domainName.charAt(0).toUpperCase() + domainName.slice(1);
      } catch {
        return url.trim();
      }
    }
  }

  function formatUrl(url) {
    try {
      const replacedUrl = replacePlaceholders(url);
      return new URL(replacedUrl.trim()).href;
    } catch {
      return `https://${replacePlaceholders(url.trim())}`;
    }
  }
</script>

<section id="your_links">
  {$i18n?.links_txt}
  <hr>
  <div aria-label="list" class={edit ? "grid gap" : "flex wrap gap"}>
    {#if edit}
      {#if Array.isArray($urls) && $urls.length > 0}
        {#each $urls as url, index}
          <div class="flex gap">
            <input checked={selected.includes(index)} type="checkbox"
              on:change={() => delete_list(index)} />
            <textarea
              on:keydown={(e) => { if (e.key === 'Enter') e.preventDefault(); }}
              placeholder={$i18n?.textarea}
              title="https://example.com/search?q=[name]"
              rows="2"
              on:input={(event) => updateUrl(event, index)}
              on:blur={() => handleBlur(index)}
            >{url}</textarea>
          </div>
        {/each}
        <div class="flex gap wrap">
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
      <input type="button" value="✎" on:click={() => { edit = !edit }} title="edit">
      <hr>
      {#each response.url as url}
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
div[aria-label="list"] {
  column-gap: .3em;
  input {
    zoom: 1.5;
    &:checked + textarea {
      color: red;
    }
  }
}
</style>
