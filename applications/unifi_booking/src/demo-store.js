import { randomUUID } from 'node:crypto';
import { transitionRoom, workflowProgress } from './domain.js';

const now = new Date().toISOString();
const rooms = [
  {id:'villa-1',name:'Villa 1',kind:'guest',state:'ready',x:8,y:12,w:25,h:32,door_ids:['front-1'],updated_at:now},
  {id:'villa-2',name:'Villa 2',kind:'guest',state:'occupied',x:38,y:12,w:25,h:32,door_ids:['front-2','patio-2'],updated_at:now},
  {id:'office',name:'Staff office',kind:'staff',state:'staff',x:68,y:12,w:24,h:20,door_ids:['office'],updated_at:now},
  {id:'villa-3',name:'Villa 3',kind:'exclusive',state:'exclusive',x:8,y:53,w:35,h:34,door_ids:['front-3'],updated_at:now},
  {id:'garage',name:'Garage',kind:'utility',state:'utility',x:48,y:53,w:44,h:34,door_ids:['gate','garage'],updated_at:now}
];
const bookings=[{id:'bk-1',room_id:'villa-2',guest_name:'Katrin Saar',email:'katrin@example.com',start_at:now,end_at:new Date(Date.now()+86400000).toISOString(),status:'checked_in',credential_delivery:['qr','pin']}];
const tasks=[{id:'t-1',room_id:'villa-3',title:'Check minibar',group:'cleaning',status:'open',hidden_until:null},{id:'t-2',room_id:'villa-3',title:'Inspect smoke detector',group:'inspection',status:'done',hidden_until:null}];
const audit=[];

export const store={
  snapshot(){return {rooms,bookings,tasks,audit:audit.slice(-30).reverse(),stats:{ready:rooms.filter(r=>r.state==='ready').length,occupied:rooms.filter(r=>r.state==='occupied').length,attention:rooms.filter(r=>['needs_attention','cleaning','inspection','maintenance'].includes(r.state)).length,progress:workflowProgress(tasks)}}},
  transition(id,event,actor='operator',reason='Manual action'){const i=rooms.findIndex(r=>r.id===id); if(i<0) throw new Error('Room not found'); const before=rooms[i].state; rooms[i]=transitionRoom(rooms[i],event); audit.push({id:randomUUID(),at:new Date().toISOString(),actor,action:event,target:id,reason,before,after:rooms[i].state}); return rooms[i]},
  completeTask(id,actor='operator'){const task=tasks.find(t=>t.id===id); if(!task) throw new Error('Task not found'); task.status='done'; audit.push({id:randomUUID(),at:new Date().toISOString(),actor,action:'task_completed',target:id,reason:task.title}); return task}
};
