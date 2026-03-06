<script>
  import { page } from '$app/stores';
  import { fav, view } from '$lib/movie/scripts/favorite';

  export let i18n, id

  import Back from "$lib/movie/image/back.svg?raw";
  import Share from "$lib/movie/image/share.svg?raw";
  import Like from "$lib/movie/image/like.svg?raw";
</script>


<header class="flex wrap gap">
  <a class="flex _center gap" href={$page.data.base + '/s_all'}>
    {@html Back} {$i18n?.back}</a>

  <button 
    class="flex _center gap _2" 
    class:like={$view?.[$page.params.what]?.includes(id)} 
    on:click={() => fav().save($page.params.what, id)}>
    {@html Like} {$i18n?.like}
  </button>

  <button 
    class="flex _center gap _2" 
    on:click={() => navigator.share({ url: $page.url.origin + $page.url.pathname })}>
    {@html Share} {$i18n?.share}
  </button>
</header>


<style lang="scss">
  .like {color: red !important;}

  header {
    background: #000;
    color-scheme: dark;
    padding: 5px 10px;
  }

  button, a {
    font-size: 14px;
    background: #333;
    color: #fff;
    padding: 5px 10px;
    border: 0;
    text-decoration: none;
    font-weight: bolder;
    border-radius: 3px;
    &:hover {
      background: #555;}
    &:active {
      background: #999 !important;
      filter: blur(1px);}
  }
</style>