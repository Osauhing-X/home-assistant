<script>
  import { language } from '$lib/config';
  export let items = [];
  export let selectedMonth = '';

  const now = new Date();
  const today = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
  let monthYear = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}`;
  let year = now.getFullYear();
  let hoveredMonth = null;
  const labels = {
    et:{months:['Jaan','Veebr','Märts','Apr','Mai','Juun','Juuli','Aug','Sept','Okt','Nov','Dets'],days:['E','','K','','R','','P'],year:'Aastavaade',title:'Vaatamiskalender',today:'Täna',saved:'Salvestus',selected:'Valitud kuu'},
    en:{months:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],days:['M','','W','','F','','S'],year:'Year view',title:'Watch calendar',today:'Today',saved:'Saved',selected:'Selected month'}
  };
  $: copy=labels[$language]||labels.et;

  function buildHeatmap(value) {
    const first = new Date(value,0,1);
    const offset = first.getDay()===0?6:first.getDay()-1;
    const days=Array(offset).fill(null);
    for(let date=new Date(value,0,1);date<=new Date(value,11,31);date.setDate(date.getDate()+1)){
      const iso=`${value}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
      days.push({iso,m:date.getMonth(),count:items.filter(item=>item.date===iso).length});
    }
    const weeks=Array.from({length:Math.ceil(days.length/7)},(_,index)=>days.slice(index*7,index*7+7));
    const header=[];let previous=-1;
    weeks.forEach(week=>{const month=week.find(Boolean)?.m;if(month!==previous)header.push({month,span:1});else header[header.length-1].span++;previous=month});
    return {weeks,header};
  }
  function selectMonth(month){selectedMonth=`${year}-${String(month+1).padStart(2,'0')}`;monthYear=selectedMonth}
  function selectToday(){year=now.getFullYear();monthYear=`${year}-${String(now.getMonth()+1).padStart(2,'0')}`;selectedMonth=''}
  function changeMonth(event){monthYear=event.currentTarget.value;const [nextYear,nextMonth]=monthYear.split('-').map(Number);if(nextYear){year=nextYear;selectedMonth=`${nextYear}-${String(nextMonth).padStart(2,'0')}`}}
  $: heatmap=buildHeatmap(year);
</script>

<section class="heatmap">
  <header><div><span class="eyebrow">{copy.year}</span><h2>{copy.title}</h2></div><div class="controls"><input type="month" value={monthYear} on:change={changeMonth} aria-label={copy.title}><button class:active={!selectedMonth} on:click={selectToday}>{copy.today}</button></div></header>
  <div class="scroll"><table class="map"><thead><tr><th></th>{#each heatmap.header as month}<th colspan={month.span} class:active={selectedMonth===`${year}-${String(month.month+1).padStart(2,'0')}`} class:hovered={hoveredMonth===month.month} on:mouseenter={()=>hoveredMonth=month.month} on:mouseleave={()=>hoveredMonth=null} on:click={()=>selectMonth(month.month)}>{copy.months[month.month]}</th>{/each}</tr></thead><tbody>{#each copy.days as day,index}<tr><td class="weekday">{day}</td>{#each heatmap.weeks as week}<td>{#if week[index]}<button title={week[index].iso} class:event={week[index].count} class:today={week[index].iso===today} class:selected={selectedMonth===week[index].iso.slice(0,7)} class:hovered={hoveredMonth===week[index].m} on:mouseenter={()=>hoveredMonth=week[index].m} on:mouseleave={()=>hoveredMonth=null} on:click={()=>selectMonth(week[index].m)}></button>{:else}<i></i>{/if}</td>{/each}</tr>{/each}</tbody></table></div>
  <div class="legend"><span><i class="event"></i>{copy.saved}</span><span><i class="today"></i>{copy.today}</span><span><i class="selected"></i>{copy.selected}</span></div>
</section>

<style>
  .heatmap{padding:22px;background:var(--panel);border:1px solid var(--line);border-radius:18px}.heatmap header{display:flex;align-items:end;justify-content:space-between;gap:16px}.heatmap h2{margin:0}.controls{display:flex;gap:8px}.controls input,.controls button{border:1px solid var(--line);background:#1d1d23;color:white;border-radius:8px;padding:7px 9px}.controls button{cursor:pointer}.controls button.active{color:#ff6262;border-color:#ff626266}.scroll{overflow-x:auto;margin-top:17px}.map{border-collapse:collapse;table-layout:fixed;min-width:744px}.map th,.map td{padding:0;text-align:center}.map thead th{height:20px;color:var(--muted);font-size:9px;font-weight:600;cursor:pointer}.map thead th.active{color:#d7ae5c}.map thead th.hovered{color:white}.weekday{width:24px;padding-right:7px!important;color:var(--muted);font-size:9px}.map td button,.map td i{display:block;width:11px;height:11px;margin:1.5px;border:0;border-radius:2px;background:#292930}.map td i{visibility:hidden}.map td button{cursor:pointer}.map td button.event{background:#3787db}.map td button.today{background:#e54b4b;outline:1px solid #ff8b8b}.map td button.selected{box-shadow:inset 0 0 0 2px #f4b94254}.map td button.hovered:not(.event):not(.today){background:#34343d}.legend{display:flex;flex-wrap:wrap;gap:14px;color:var(--muted);font-size:10px;margin-top:8px;padding:0}.legend span{display:flex;align-items:center;gap:5px}.legend i{width:9px;height:9px;background:#292930;border-radius:2px}.legend i.event{background:#3787db}.legend i.today{background:#e54b4b}.legend i.selected{background:#f4b94254}@media(max-width:700px){.heatmap{padding:14px}.heatmap header{align-items:start}.controls{flex-wrap:wrap;justify-content:end}}
</style>
