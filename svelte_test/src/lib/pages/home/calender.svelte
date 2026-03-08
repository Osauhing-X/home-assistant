<script>
  import Grid from '$lib/components/grid.svelte'
  import Calender from '$lib/pages/calender/module.svelte';
  import Card from '$lib/pages/movie/components/poster.svelte'

  import { calender, selected, selectedYM } from "$lib/pages/calender/calender_store";
    import { goto } from '$app/navigation';
  
  let monthYear, open = false


  function formatDate(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }
    // Päevade arv tänasest sündmuseni
  function daysLeft(dateStr) {
    const today = new Date(formatDate(new Date()));
    const target = new Date(dateStr);
    return Math.ceil((target - today) / (1000 * 60 * 60 * 24));
  }

  let active = null

  function removeEvent(event) {
    calender.update(list => {
      const updated = list.filter(e => e !== event); // eemaldab täpse objekti
      localStorage.setItem("save:calender", JSON.stringify(updated));
      return updated;
    });
  }

</script>


<center class="grid">
  <details class="grid gap _2" bind:open>
    <summary class="flex _wrap gap _space">
      <h2>Calender</h2>
      <input type="month" value={monthYear} on:change={(e) => {
          const [yy, mm] = e.target.value.split('-').map(Number);
          $selectedYM = { year: yy, month: mm - 1 }; }} />
    </summary>

    <section class="grid gap _3">

    
    <Calender bind:monthYear />

    {#if $selected.length}
      <div overflow>
        <table>
          <thead>
            <tr>
              <th></th>
              <th>title</th>
              <th>description</th>
              <th>days_left</th>
              <th>expire</th>
            </tr>
          </thead>
          <tbody>
            {#each $selected as e, i}
              <tr on:click={() => active = active == i ? null : i}>
                <td> <picture> <img src={e.img} alt="poster" style="max-width: 40px;"> </picture> </td>
                <td>{e.title}</td>
                {#if active == i}
                  <td colspan="3">
                    <div class="flex wrap gap _2">
                      <button on:click={() => removeEvent(e)}>Remove</button>
                      <button on:click={() => goto(e.url)}>Url</button>
                    </div>
                  </td>
                {:else}
                  <td>{e.description}</td>
                  <td>{daysLeft(e.date)}</td>
                  <td>{new Date(e.date).getDate()}.{new Date(e.date).getMonth() + 1}.{new Date(e.date).getFullYear()}</td>
                {/if}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <p>none</p>
    {/if}
  </section>
</details>


  {#if !open && $selected.length}
    <Grid data-sveltekit-preload-data="tap" padding="0" column="135">
      {#each $selected as {id, group, img}}
        {#if id && group && img}
          <Card object={{id, "poster_path": img, "media_type": group}} />
        {/if}
      {/each}
    </Grid>
  {/if}

</center>


<style>
details {
  --p: 0;
}
  summary {
    cursor: pointer;
    list-style: none;
  }


  
  
/* --- # TABLE */

  div[overflow] {
  overflow-x: auto; /* horisontaalne kerimine väiksemal ekraanil */
}

table {
  width: 100%;
  border-collapse: collapse;
  font-family: sans-serif;
  min-width: 600px; /* tagab kerimise, kui väike ekraan */
}

thead {
  background-color: #f0f0f0;
}

thead th {
  text-align: left;
  padding: 12px 15px;
  font-weight: 600;
  border-bottom: 2px solid #ddd;
}

tbody td {
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
}

tbody tr:hover {
  background-color: #fafafa;
}

img {
  display: block;
  max-width: 40px;
  height: auto;
  border-radius: 4px;
}

td, th {
  white-space: nowrap; /* hoiab teksti ühel real, tabel kerib vajadusel */
}
</style>