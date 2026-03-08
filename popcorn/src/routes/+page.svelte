<script>
  
  import { selected } from "$lib/pages/calender/calender_store";


  import Movies from '$lib/pages/home/movies.svelte';
  import Calender from "$lib/pages/home/calender.svelte";



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
