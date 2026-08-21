const $=s=>document.querySelector(s); let data,selected;
const labels={ready:'Ready',reserved:'Reserved',occupied:'Occupied',cleaning:'Cleaning',inspection:'Inspection',maintenance:'Maintenance',needs_attention:'Needs attention',exclusive:'Exclusive',staff:'Staff',utility:'Utility'};
async function api(path,init){const r=await fetch(path,{headers:{'content-type':'application/json'},...init});const x=await r.json();if(!r.ok)throw new Error(x.error);return x}
function render(){
  $('#stats').innerHTML=[['Ready spaces',data.stats.ready],['Occupied',data.stats.occupied],['Needs attention',data.stats.attention],['Task progress',`${data.stats.progress}%`]].map(([x,y])=>`<div class="stat"><small>${x}</small><b>${y}</b></div>`).join('');
  const states=[...new Set(data.rooms.map(r=>r.state))];$('#legend').innerHTML=states.map(s=>`<span><i class="${s}"></i>${labels[s]}</span>`).join('');
  $('#map').innerHTML=data.rooms.map(r=>`<button class="room ${r.state}" data-id="${r.id}" style="left:${r.x}%;top:${r.y}%;width:${r.w}%;height:${r.h}%">${r.name}<small>${labels[r.state]}</small></button>`).join('');
  $('#tasks').innerHTML=data.tasks.length?data.tasks.map(t=>`<div class="task ${t.status}" data-task="${t.id}"><b>${t.title}</b><p>${t.room_id} · ${t.group}</p>${t.status==='done'?'':`<button>Complete</button>`}</div>`).join(''):'<p>No open tasks</p>';
  $('#audit').innerHTML=data.audit.length?data.audit.map(a=>`<div class="activity"><time>${new Date(a.at).toLocaleString()}</time><div><b>${a.actor} · ${a.action.replaceAll('_',' ')}</b><p>${a.target} — ${a.reason}</p></div></div>`).join(''):'<p>No operator actions yet.</p>';
  document.querySelectorAll('.room').forEach(b=>b.onclick=()=>openRoom(b.dataset.id));document.querySelectorAll('.task button').forEach(b=>b.onclick=()=>complete(b.parentElement.dataset.task));
}
function openRoom(id){selected=data.rooms.find(r=>r.id===id);$('#roomName').textContent=selected.name;$('#roomKind').textContent=selected.kind.toUpperCase();$('#roomState').textContent=`Current state: ${labels[selected.state]}`;$('#dialogError').textContent='';$('#roomDialog').showModal()}
async function refresh(){data=await api('/api/snapshot');render()}
async function complete(id){await api(`/api/tasks/${id}/complete`,{method:'POST',body:JSON.stringify({actor:'Local operator'})});refresh()}
$('#applyAction').onclick=async()=>{try{await api(`/api/rooms/${selected.id}/transition`,{method:'POST',body:JSON.stringify({event:$('#roomEvent').value,actor:'Local operator',reason:$('#roomReason').value})});$('#roomDialog').close();refresh()}catch(e){$('#dialogError').textContent=e.message}};
refresh();
