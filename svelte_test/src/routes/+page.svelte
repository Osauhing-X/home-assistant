<script>
  
  import { selected } from "$lib/pages/calender/calender_store";


  import Movies from '$lib/pages/home/movies.svelte';
  import Calender from "$lib/pages/home/calender.svelte";


   import { resolve } from '$app/paths';

  function goToMovies() {
    window.location.href = resolve('/s_all');
  }

    function goToMovies2() {
    window.location.assign(resolve('/sv'))
  }


    function goToMovies3() {
    window.location.replace(resolve('/sv'));
  }

  import { base } from '$app/paths';

  function navigate(path) {
    window.location.href = `${base}${path}`;
  }
</script>


<svelte:head>
  <style>
    body > div {
      display: grid !important;
      row-gap: 3em;
      padding: 3em 0; }
  </style>
</svelte:head>


<Movies />

<hr>

<Calender />

<hr>

<center class="flex wrap gap">
  <button on:click={goToMovies}>Test 1</button>
  <button on:click={() => navigate('/s_all')}>Test 2</button>
  <button on:click={goToMovies2}>test 3</button>
  <button on:click={goToMovies3}>test 4</button>
</center>