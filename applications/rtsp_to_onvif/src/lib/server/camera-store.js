import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {writePrivateFile} from './private-file.js';
export const defaults={discoveryPort:3702,onvifPort:8091,rtspPort:8554,autoDiscovery:true,offlineNotifications:true,fragmentMs:100,gop:5,buffering:false};
const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
const cameraList=value=>Array.isArray(value)&&value.every(row=>object(row)&&typeof row.id==='string'&&row.id.length>0);

// One RTSP application process per directory. Updates include their read inside
// the lock, so discovery/DHCP callbacks cannot overwrite simultaneous GUI edits.
export function createCameraStore(directory){
 const files={cameras:path.join(directory,'cameras.json'),settings:path.join(directory,'settings.json')},locks=new Map();
 const valid=(kind,value)=>kind==='cameras'?cameraList(value):object(value);
 async function read(kind){
  let source;try{source=await readFile(files[kind],'utf8');}catch(error){if(error.code==='ENOENT')return kind==='cameras'?[]:{};throw Error('RTSP configuration could not be read; existing data has not been replaced.');}
  let result;try{result=JSON.parse(source);}catch{throw Error('RTSP configuration is invalid; restore a verified backup. Existing data has not been replaced.');}
  if(!valid(kind,result))throw Error('RTSP configuration has an invalid structure; existing data has not been replaced.');return result;
 }
 async function transaction(kind,action){
  const previous=locks.get(kind)||Promise.resolve();let release;const gate=new Promise(resolve=>{release=resolve;}),tail=previous.then(()=>gate);locks.set(kind,tail);await previous;
  try{return await action();}finally{release();if(locks.get(kind)===tail)locks.delete(kind);}
 }
 async function write(kind,value){
  if(!valid(kind,value))throw Error('Invalid RTSP configuration update');
  await read(kind); // Never overwrite corrupt or inaccessible existing storage.
  await writePrivateFile(files[kind],JSON.stringify(value,null,2));
 }
 return {
  cameras:()=>read('cameras'),
  save:value=>transaction('cameras',()=>write('cameras',value)),
  updateCameras:action=>transaction('cameras',async()=>{const all=await read('cameras'),before=JSON.stringify(all),result=await action(all);if(JSON.stringify(all)!==before)await write('cameras',all);return result;}),
  settings:async()=>({...defaults,...await read('settings')}),
  saveSettings:value=>transaction('settings',async()=>{
   if(!object(value))throw Error('Invalid RTSP settings update');
   const clean={discoveryPort:Math.min(65535,Math.max(1,Number(value.discoveryPort)||3702)),onvifPort:Math.min(65535,Math.max(1024,Number(value.onvifPort)||8091)),rtspPort:Math.min(65535,Math.max(1024,Number(value.rtspPort)||8554)),autoDiscovery:value.autoDiscovery!==false,offlineNotifications:value.offlineNotifications!==false,fragmentMs:Math.min(2000,Math.max(50,Number(value.fragmentMs)||100)),gop:Math.min(300,Math.max(1,Number(value.gop)||5)),buffering:Boolean(value.buffering)};
   await write('settings',clean);return clean;
  })
 };
}
