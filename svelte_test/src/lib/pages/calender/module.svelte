<script>
  import { writable, derived } from 'svelte/store';
  import { calender } from "$lib/pages/calender/calender_store";

// --- # Language
  import language_pack from '$lib/pages/calender/i18n.json'
  import { request } from '$lib/assets/request';
  let i18n = request('auto', language_pack)


  let monthYear = '';

  // Kuupäev formaadi funktsioon ilma ajavööndi nihketa
  function formatDate(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  // Writables
  const selectedYM = writable({ year: new Date().getFullYear(), month: new Date().getMonth() });
  let hoveredMonth = null;

  // monthYear koostatakse valitud aasta ja kuu põhjal
  $: {
    const mm = String($selectedYM.month + 1).padStart(2, '0');
    monthYear = `${$selectedYM.year}-${mm}`;
  }

  $: daysOfWeek = $i18n?.week ?? [] ; // esmasp - pühap
  $: months = $i18n?.month ?? [];
  const todayISO = formatDate(new Date());

  // Laeme andmed localStorage-st
  import { browser } from '$app/environment';
  let stored
  if(browser) stored = localStorage.getItem("save:calender");
  if (stored) calender.set(JSON.parse(stored));

  // Heatmapi koostamine: nädal algab esmaspäevast ja kuu algab aasta esimesest päevast
  function buildHeatmap(year) {
    const firstDate = new Date(year, 0, 1);
    const jsDay = firstDate.getDay(); // 0=pühapäev ... 6=laup
    const offset = jsDay === 0 ? 6 : jsDay - 1; // nihutame nii, et esmasp=0, pühap=6

    let days = Array(offset).fill(null);

    let date = new Date(year, 0, 1);
    const end = new Date(year, 11, 31);

    while (date <= end) {
      days.push({
        d: date.getDate(),
        m: date.getMonth(),
        y: date.getFullYear(),
        iso: formatDate(date)
      });
      date.setDate(date.getDate() + 1);
    }

    const weeks = Array.from({ length: Math.ceil(days.length / 7) }, (_, i) =>
      days.slice(i * 7, i * 7 + 7)
    );

    // Koostame headeri kuude kaupa (spanidega)
    const header = [];
    let prevMonth = -1;
    weeks.forEach(w => {
      let m = w.find(d => d)?.m;
      if (m !== prevMonth) header.push({ name: months[m], span: 1, nr: m });
      else header[header.length - 1].span++;
      prevMonth = m;
    });

    return { weeks, header };
  }

  // Sünkroniseerime calender store ja heatmap
  $: events = $calender;
  $: heatmap = buildHeatmap($selectedYM.year);

  // Filtreerime sündmused valitud aasta ja kuu järgi
  const filteredEvents = derived(
    [calender, selectedYM],
    ([$calender, $selectedYM]) =>
      $calender.filter(e => {
        const [y, m] = e.date.split('-').map(Number);
        return y === $selectedYM.year && m === $selectedYM.month + 1;
      })
  );

  // Eemaldame sündmuse
  function removeEvent(event) {
    calender.update(list => {
      const updated = list.filter(e => e !== event); // eemaldab täpse objekti
      localStorage.setItem("save:calender", JSON.stringify(updated));
      return updated;
    });
  }


  // Päevade arv tänasest sündmuseni
  function daysLeft(dateStr) {
    const today = new Date(formatDate(new Date()));
    const target = new Date(dateStr);
    return Math.ceil((target - today) / (1000 * 60 * 60 * 24));
  }

  // Kuude värvid (näide)
  const months_color = m => (m % 2 ? 'odd' : 'even');

  import Pop from '$lib/pages/calender/add_date.svelte'
</script>

<style lang="scss">
  .scroll {
    overflow-x: auto;
    max-width: 100vw;

    caption {
      text-align: start;
      margin-bottom: 1em;
      :global(> input) {
        position: sticky;
        left: 0px; }
    }
    
  }
  
  table { border-collapse: collapse; }
  td, th { padding: 0; margin: 0; text-align: center; }
  .day { width: 15px; height: 15px; cursor: pointer; }
  .label { font-size: 10px; color: #ccc; }
  
  .event-table th, .event-table td { padding: 4px 8px; text-align: left; }

  
  

  table.map {
    user-select: none;
    thead {
      th {
        color: #ccc;

        &.active { color: red;}
        &.hover { color: blue;}
    } }
    tbody {
    border: 1px solid transparent;

    td {
      border: 1px solid transparent;

      > div {
        box-shadow: inset 0 0 0 1px var(--base), inset 0 0 0 var(--border, 2px) var(--color, transparent);
        &.active { --color: light-dark(#333, #999)}

        &.event:not(.today){ --color: light-dark(#1b6b1e, #5cc726); --border: 4px }
        

        &.today.event {
          background-image: -webkit-linear-gradient(45deg, red 50%, light-dark(#1b6b1e, #5cc726) 50%); }
        &.today:not(.event){
          background: red;}
        

        backdrop-filter: contrast(var(--number));
        &.odd { --number: .3;}
        &.even { --number: .6;}
        
      //  &:hover {}
    } } }
  }

#events {
  width: 100%;
  border: 1px solid var(--transparent);

  th { background: var(--transparent); }
  tr:nth-child(even) td:not(:first-of-type, :last-of-type) {
    background: var(--default); }
  th:not(:empty) {
    text-align: start;
    padding-left: 1em; } }
</style>

<center class="top bottom grid gap _5 padding">
<section class="scroll">
  <table class="map">
    <caption>
      <label>{$i18n?.input}
      <input type="month" value={monthYear} on:change={(e) => {
          const [yy, mm] = e.target.value.split('-').map(Number);
          selectedYM.set({ year: yy, month: mm - 1 }); }} />
      </label>
      <Pop i18n={request('auto', language_pack)}/>
    </caption>
    <thead>
      <tr>
        <th></th>
        {#each heatmap.header as m}
          <th
          class:hover={hoveredMonth === months.indexOf(m.name)}
          class:active={$selectedYM.month === months.indexOf(m.name)}
            colspan={m.span}
            class="label"
            on:mouseenter={() => hoveredMonth = months.indexOf(m.name)}
            on:mouseleave={() => hoveredMonth = null} >
            {months[m.nr]}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each daysOfWeek as d, i}
        <tr>
          <td class="label" null>{d}</td>
          {#each heatmap.weeks as w}
            <td null>
              {#if w[i]}
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div
                  class="day {months_color(w[i].m)}"
                  title={w[i].iso}
                  class:event={$calender.some(e => e.date === w[i].iso)}
                  class:today={w[i].iso === todayISO}
                  class:active={$selectedYM.month === w[i].m}
                  class:hover={hoveredMonth === w[i].m}
   
                  on:mouseenter={() => hoveredMonth = w[i].m}
                  on:mouseleave={() => hoveredMonth = null}
                  on:click={() => {
                    const [y, m] = w[i].iso.split('-').map(Number);
                    selectedYM.set({ year: y, month: m - 1 });
                  }}
                ></div>
              {:else}
                <div class="day" style="opacity:0.1"></div>
              {/if}
            </td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</section>

<section>
<h3>{$i18n?.select} {months[$selectedYM.month]} {$selectedYM.year}</h3>
{#if $filteredEvents.length}
  <table border="1" class="event-table" id="events">
    <thead>
      <tr>
        <th>{$i18n?.title}</th>
        <th>{$i18n?.description}</th>
        <th>{$i18n?.days_left}</th>
        <th>{$i18n?.expire}</th>
      </tr>
    </thead>
    <tbody>
      {#each $filteredEvents as e, i}
        <tr>
          <td>
            {e.title}
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <!-- svelte-ignore a11y_missing_attribute -->
            (<a style="cursor: pointer;" on:click={() => removeEvent(e)}>remove</a>)
          </td>
          <td>{e.description}</td>
          <td>{daysLeft(e.date)}</td>
          <td>{new Date(e.date).getDate()}.{new Date(e.date).getMonth() + 1}.{new Date(e.date).getFullYear()}</td>
        </tr>
      {/each}
    </tbody>
  </table>

{:else}
  <p>{$i18n?.none}</p>
{/if}
</section>
</center>