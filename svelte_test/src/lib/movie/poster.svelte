<!-- SCRIPT ### -->
<script>
  import { view } from '$lib/movie/discover_store.js'
  import { page } from '$app/stores';
  import { list_db } from "$lib/movie/themoviedb_store";
  import In_View from "$lib/components/in_view.svelte"

  export let object = null;
  export let show = true;

  let image = object?.poster_path || object?.profile_path || null

  async function load(){ return 'https://image.tmdb.org/t/p/w500' +  image}


    import { language } from '$lib/assets/language.js';
    let param = $page.url.searchParams.get('language');
    let lang = !param 
      ? '?language=' + $language
      : param != 'en'
      ? '?language=' + param : ""


     import Image from '$lib/components/image.svelte'
  </script>
  
  <!-- CONTENT ### -->
  {#await load() then src}
    {#if object && image}
      <In_View id={object.id} href="/{object.media_type}/{object.id}{lang}" tag='a'>
        <Image {src} alt={null} />
        
        {#if show && $view?.[object?.media_type]?.includes(object?.id)}
          <link class="like" />
        {/if}
      </In_View>
    {/if}
  {/await}


<style>


  link { display: block;}
  link.like::before {
    content: '❤︎';
    color: light-dark(red, var(--primary));
    position: absolute;
    top: 0;
    right: 0;
    background: var(--base);
    padding: 0 0 4px 7px;
    border-radius: 0 0 0 50%;
    font-size: 20px;
    line-height: 20px;
  }
</style>

