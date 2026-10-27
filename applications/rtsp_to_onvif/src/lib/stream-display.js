export function displayStreamUrl(value){
 try{const url=new URL(value);if(!['rtsp:','rtsps:'].includes(url.protocol))return 'Configured RTSP source';const query=Boolean(url.search);url.username='';url.password='';url.search='';url.hash='';return url.href+(query?'?…':'');}catch{return 'Configured RTSP source';}
}
