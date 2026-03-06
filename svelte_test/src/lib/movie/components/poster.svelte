<!-- SCRIPT ### -->
<script>
  import { list_db } from "$lib/movie/scripts/themoviedb_store";
  import { view } from '$lib/movie/scripts/favorite'

  import { page } from '$app/stores';
  
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
      <In_View id={object.id} href="{$page.data.base + "/" + object.media_type}/{object.id}{lang}" tag='a'>
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
    color: red;
    background: #fff;
    position: absolute;
    top: 0;
    right: 0;
    padding: 0 0 5px 7px;
    border-radius: 0 0 0 50%;
    font-size: 20px;
    line-height: 20px;
    text-shadow: 
      0 0 5px #000,
      0 0 5px #000,
      0 0 5px #000,
      0 0 5px #000;
  }
</style>

