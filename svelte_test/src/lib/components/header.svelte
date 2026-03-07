<script>
  import { page } from '$app/stores';
  import { fav, view } from '$lib/pages/movie/scripts/favorite';

  import SVG from '$lib/assets/header.svg?raw'

  import { request } from '$lib/assets/request'
  let i18n = request('header')

  $: what = $page.params.what
  $: where = $page.params?.where
  $: like = $view?.[what]?.includes(where)
  $: back = $page?.params?.search ? '/' : '/s_all' + $page.url.search

    
</script>


<header class="grid">
  {@html SVG}
  <section class="flex wrap gap">
    <a class="flex _center gap _2" href={$page.data.base + back}>
      <svg width="24" height="24" fill="currentColor"> <use href="#back"></use> </svg>
      <strong>{$i18n?.back}</strong>
    </a>

    {#if $page.params?.where}
      <button popovertarget="new_date" class="flex _center gap _2">
        <svg width="24" height="24" fill="currentColor"> <use href="#calender"></use> </svg>
        <strong>{$i18n?.date}</strong>
      </button>

      <button on:click={() => fav().save(what, where)} class="flex _center gap _2" class:like >
        <svg width="24" height="24" fill="currentColor"> <use href="#like"></use> </svg>
        <strong>{$i18n?.like}</strong>
      </button>
    {/if}

    {#if $page.params?.search}
      <button popovertarget="search_popover" class="flex _center gap">
        <svg width="24" height="24" fill="currentColor"> <use href="#search"></use> </svg>
        <strong>{$i18n?.search}</strong>
      </button>

      <a class="flex _center gap _2 orange" href={$page.data.base + '/favorite'}>
        <svg width="24" height="24" fill="currentColor"> <use href="#favorite"></use> </svg>
        <strong>{$i18n?.fav}</strong>
      </a>
    {/if}

    
  </section>

  <slot />
</header>


<style lang="scss">
  .like, .orange:hover {color: orange !important;}

  header {
    section {
      background: #000;
      color-scheme: dark;
      padding: 5px 10px;
    }
  }

  strong {
    font-size: 14px;
    @media (max-width: 800px){
      display: none; }
    @media (min-width: 800px){
      margin-right: 5px; }
  }
  button, a {
    
    background: #333;
    color: #fff;
    padding: 5px;
    border: 0;
    text-decoration: none;
    border-radius: 3px;
    &:hover {
      background: #555;}
    &:active {
      background: #999 !important;
      filter: blur(1px);}
  }
</style>