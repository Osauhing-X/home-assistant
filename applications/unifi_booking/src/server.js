import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { store } from './demo-store.js';

const root=join(fileURLToPath(new URL('..',import.meta.url)),'public');
const port=Number(process.env.PORT||8099);
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml'};
const json=(res,status,data)=>{res.writeHead(status,{'content-type':'application/json; charset=utf-8','cache-control':'no-store'});res.end(JSON.stringify(data))};
const body=async req=>{let s='';for await(const c of req){s+=c;if(s.length>1e6)throw new Error('Payload too large')}return s?JSON.parse(s):{}};

const server=http.createServer(async(req,res)=>{try{
  const url=new URL(req.url,'http://addon.local');
  if(url.pathname==='/api/health')return json(res,200,{ok:true,mode:'demo'});
  if(url.pathname==='/api/snapshot'&&req.method==='GET')return json(res,200,store.snapshot());
  let m=url.pathname.match(/^\/api\/rooms\/([^/]+)\/transition$/);
  if(m&&req.method==='POST'){const b=await body(req);return json(res,200,store.transition(decodeURIComponent(m[1]),b.event,b.actor,b.reason))}
  m=url.pathname.match(/^\/api\/tasks\/([^/]+)\/complete$/);
  if(m&&req.method==='POST'){const b=await body(req);return json(res,200,store.completeTask(decodeURIComponent(m[1]),b.actor))}
  if(url.pathname.startsWith('/api/'))return json(res,404,{error:'Not found'});
  const rel=url.pathname==='/'?'index.html':url.pathname.slice(1); const safe=normalize(rel).replace(/^(\.\.[\\/])+/, ''); const file=join(root,safe); if(!file.startsWith(root))return json(res,403,{error:'Forbidden'}); const data=await readFile(file);res.writeHead(200,{'content-type':mime[extname(file)]||'application/octet-stream'});res.end(data);
}catch(e){if(e.code==='ENOENT')return json(res,404,{error:'Not found'});json(res,400,{error:e.message})}});
server.listen(port,'0.0.0.0',()=>console.log(`UniFi Booking listening on ${port}`));
