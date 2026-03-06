<script>
  import { page } from '$app/stores';
  import { fav, view } from '$lib/movie/scripts/favorite';

  export let i18n

  import Back from "$lib/movie/image/back.svg?raw";
  import Favorite from "$lib/movie/image/favorite.svg?raw";
</script>


<header class="flex wrap gap">
  <a class="flex _center gap" href={$page.data.base + '/s_all'}>
    {@html Back} {$i18n?.back}</a>
</header>


<style lang="scss">
  header {
    background: #000;
    color-scheme: dark;
    padding: 5px 10px;
  }

  a {
    background: #333;
    color: #fff;
    padding: 5px 10px;
    border: 0;
    text-decoration: none;
    font-weight: bolder;
    font-size: 14px;
    border-radius: 3px;
    &:hover {
      background: #555;}
    &:active {
      background: #999 !important;
      filter: blur(1px);}
  }
</style>