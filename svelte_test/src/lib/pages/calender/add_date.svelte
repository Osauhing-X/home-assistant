<script>
  import { calender } from "./calender_store";

// --- # Language
  export let i18n


  $: innerWidth = 0
  
  let today = new Date().toISOString().split('T')[0];
  export let
    date = today,
    title = null,
    description = null;


  function add(){
    let input = {date, title, description}

    let local = JSON.parse(localStorage.getItem('save:calender')) || []
        local = [...local, input]

    $calender = [...$calender, input]

    localStorage.setItem('save:calender', JSON.stringify(local))

    document.getElementById("Close_New_date").click();

    date = today,
    title = null,
    description = null;
  }
</script>

<svelte:window bind:innerWidth />

<input id="Close_New_date" type="button" value={$i18n?.add} popovertarget="new_date">

<pop-menu popover={innerWidth >= 800 ? 'auto' : 'manual'} id="new_date">
  <header class="flex">
    <h3>{$i18n?.add}</h3>
    <input class='close' title="close" type="button" value="✖" popovertarget='new_date' popovertargetaction="hide">
  </header>
  
  <form class="grid" on:submit|preventDefault={add}>
    
    <label class="grid gap">{$i18n?.title[0]}
      <input type="text" bind:value={title} placeholder="Title" required />
      <small>{$i18n?.title[1]}</small>
    </label>
      
      <hr>
    
    <label class="grid gap">{$i18n?.description[0]}
      <textarea bind:value={description} required rows="3" placeholder="Description"></textarea>
      <small>{$i18n?.description[1]}</small>
    </label>
      
    <hr>

    <label class="grid gap">{$i18n?.expire[0]}
      <input type="date" bind:value={date} min={today} name="date" required />
      <small>{$i18n?.expire[1]}</small>
    </label>
      
    <hr>

    <label class="grid gap">
      <input type="submit">
      <small>{$i18n?.note}</small>
    </label>

  </form>
</pop-menu>

<style>
  form { --y-axis: 10px }
  hr {width: -webkit-fill-available;}
  #new_date {
    width: min(100% - 2em, 350px);
    height: min-content;
    max-height: 70vh;
    padding: 0;
    border: 0 solid var(--black);
    border-width: 3px 1px;
  }

  #new_date > header {
    padding: 5px 5px 5px 10px;
    justify-content: space-between;
    border-bottom: 1px solid #444;
    color-scheme: dark;
    background: #000;
    font-family: monospace;
  }

  #new_date > form {
    padding: 10px;
  }

  .close {
    aspect-ratio: 1;
    padding: 0 4px;}
</style>