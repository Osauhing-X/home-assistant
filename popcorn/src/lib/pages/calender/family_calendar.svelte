<script>
  export let items = [];
  export let selectedMonth = '';

  let year = new Date().getFullYear();
  const today = new Date().toISOString().slice(0, 10);
  const monthNames = ['Jaan', 'Veebr', 'Märts', 'Apr', 'Mai', 'Juun', 'Juuli', 'Aug', 'Sept', 'Okt', 'Nov', 'Dets'];
  const weekdays = ['E', '', 'K', '', 'R', '', 'P'];

  function daysFor(y) {
    const start = new Date(y, 0, 1);
    const result = Array((start.getDay() + 6) % 7).fill(null);
    for (let date = new Date(y, 0, 1); date.getFullYear() === y; date.setDate(date.getDate() + 1)) {
      const iso = `${y}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      result.push({ iso, month: date.getMonth(), count: items.filter((item) => item.date === iso).length });
    }
    return result;
  }

  function choose(month) {
    const value = `${year}-${String(month + 1).padStart(2, '0')}`;
    selectedMonth = selectedMonth === value ? '' : value;
  }

  function changeYear(event) {
    const value = Number(event.currentTarget.value);
    if (value >= 1900 && value <= 2200) year = value;
  }

  $: days = daysFor(year);
  $: weeks = Array.from({ length: Math.ceil(days.length / 7) }, (_, index) => days.slice(index * 7, index * 7 + 7));
  $: monthStarts = monthNames.map((name, month) => ({ name, month, week: Math.floor((days.findIndex((day) => day?.month === month)) / 7) }));
</script>

<section class="heatmap">
  <header>
    <div><span class="eyebrow">Aastavaade</span><h2>Vaatamiskalender</h2></div>
    <div class="year-control">
      <label for="calendar-year">Aasta</label>
      <input id="calendar-year" type="year" inputmode="numeric" value={year} on:change={changeYear} aria-label="Kalendri aasta">
      {#if selectedMonth}<button class="clear" on:click={() => selectedMonth = ''}>Kõik kuud ×</button>{/if}
    </div>
  </header>

  <div class="heat-scroll">
    <div class="calendar">
      <div class="month-row">
        {#each monthStarts as month}
          <button style={`grid-column:${month.week + 2}`} class:active={selectedMonth === `${year}-${String(month.month + 1).padStart(2, '0')}`} on:click={() => choose(month.month)}>{month.name}</button>
        {/each}
      </div>
      <div class="weekday-row" aria-hidden="true">{#each weekdays as day}<span>{day}</span>{/each}</div>
      <div class="heat" aria-label={`Aasta ${year} kalender`}>
        {#each weeks as week}
          <div class="week">{#each Array(7) as _, index}{#if week[index]}<button title={`${week[index].iso}${week[index].count ? ` · ${week[index].count} salvestust` : ''}`} class:event={week[index].count} class:today={week[index].iso === today} class:selected={selectedMonth === week[index].iso.slice(0, 7)} on:click={() => choose(week[index].month)}><span>{week[index].count || ''}</span></button>{:else}<i></i>{/if}{/each}</div>
        {/each}
      </div>
    </div>
  </div>

  <div class="legend"><span><i class="event"></i> Salvestus</span><span><i class="today"></i> Täna</span><span><i class="selected"></i> Valitud kuu</span></div>
</section>

<style>
  .heatmap{padding:22px;background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden}.heatmap header{display:flex;align-items:end;justify-content:space-between;gap:16px}.heatmap h2{margin:0}.year-control{display:flex;align-items:center;gap:8px}.year-control label{font-size:10px;color:var(--muted);text-transform:uppercase}.year-control input,.clear{border:1px solid var(--line);background:#1d1d23;color:white;border-radius:8px;padding:7px 9px}.year-control input{width:78px}.clear{color:var(--gold);cursor:pointer}.heat-scroll{overflow-x:auto;margin-top:18px;padding-bottom:5px}.calendar{position:relative;display:grid;grid-template-columns:24px auto;grid-template-rows:20px auto;column-gap:7px;min-width:760px}.month-row{grid-column:1/-1;display:grid;grid-template-columns:24px repeat(53,11px);column-gap:3px}.month-row button{border:0;background:transparent;color:var(--muted);font-size:9px;padding:0;text-align:left;cursor:pointer}.month-row button.active{color:var(--gold);font-weight:800}.weekday-row{display:grid;grid-template-rows:repeat(7,11px);gap:3px;color:var(--muted);font-size:9px;line-height:11px}.heat{display:flex;gap:3px}.week{display:grid;grid-template-rows:repeat(7,11px);gap:3px}.week button,.week i{width:11px;height:11px;padding:0;border:0;border-radius:2px;background:#292930}.week button{cursor:pointer}.week button.event{background:#9a6a1f;box-shadow:inset 0 0 0 1px #e8b85d}.week button.today{outline:1px solid #f5f5f5;outline-offset:1px}.week button.selected{box-shadow:0 0 0 1px var(--gold)}.week button span{display:none}.legend{display:flex;flex-wrap:wrap;gap:14px;color:var(--muted);font-size:10px;margin-top:8px;padding:0}.legend span{display:flex;align-items:center;gap:5px}.legend i{display:inline-block;width:9px;height:9px;background:#292930;border-radius:2px}.legend i.event{background:#9a6a1f}.legend i.today{outline:1px solid #f5f5f5}.legend i.selected{outline:1px solid var(--gold)}@media(max-width:700px){.heatmap{padding:14px}.heatmap header{align-items:start}.year-control{flex-wrap:wrap;justify-content:end}}
</style>
