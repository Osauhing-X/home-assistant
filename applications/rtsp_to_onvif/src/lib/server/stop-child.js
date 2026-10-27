export function stopChild(child,{graceMs=3000,killWaitMs=1000}={}){
 return new Promise(resolve=>{
  if(!child?.pid||child.exitCode!==null||child.signalCode)return resolve();
  let timer,deadline,finished=false;
  const finish=()=>{if(finished)return;finished=true;clearTimeout(timer);clearTimeout(deadline);child.removeListener('close',finish);resolve();};
  child.once('close',finish);
  timer=setTimeout(()=>{try{child.kill('SIGKILL');}catch{}if(!finished)deadline=setTimeout(finish,killWaitMs);},graceMs);
  try{if(!child.kill('SIGTERM'))finish();}catch{finish();}
 });
}
