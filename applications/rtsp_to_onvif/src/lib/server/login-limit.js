export function createLoginLimit({now=Date.now,maxFailures=8,blockMs=60000,windowMs=900000,maxClients=1024,globalFailures=100}={}){
 const clients=new Map();let global={count:0,expires:0};
 function state(address){const clock=now();for(const [key,row] of clients)if(row.expires<=clock)clients.delete(key);if(global.expires<=clock)global={count:0,expires:clock+60000};return {clock,key:String(address||'unknown').slice(0,200)};}
 function check(address){const {clock,key}=state(address),row=clients.get(key);let wait=0;
  if(global.count>=globalFailures)wait=global.expires-clock;
  if(row?.blockedUntil>clock)wait=Math.max(wait,row.blockedUntil-clock);
  if(!row&&clients.size>=maxClients)wait=Math.max(wait,blockMs);
  return {allowed:wait<=0,retry_after:Math.max(0,Math.ceil(wait/1000))};
 }
 return {check,failure(address){const {clock,key}=state(address),row=clients.get(key)||{count:0,blockedUntil:0,expires:clock+windowMs};if(row.blockedUntil&&row.blockedUntil<=clock){row.count=0;row.blockedUntil=0;}row.count++;row.expires=clock+windowMs;if(row.count>=maxFailures)row.blockedUntil=clock+blockMs;if(clients.has(key)||clients.size<maxClients)clients.set(key,row);global.count++;return check(address);},success(address){clients.delete(String(address||'unknown').slice(0,200));}};
}
export const guiLoginLimit=createLoginLimit();
