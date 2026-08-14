import { mkdir,readFile,rename,writeFile } from 'node:fs/promises';
import path from 'node:path';
const dir=process.env.RTSP_ONVIF_DATA||path.join(process.env.DATA_DIR||path.resolve('.data'),'application-data','rtsp-to-onvif');
const file=path.join(dir,'cameras.json');
const settingsFile=path.join(dir,'settings.json');
const defaults={discoveryPort:3702,onvifPort:8091,rtspPort:8554,autoDiscovery:true,fragmentMs:100,gop:5,buffering:false};
export async function cameras(){try{return JSON.parse(await readFile(file,'utf8'))}catch{return[]}}
export async function save(value){await mkdir(dir,{recursive:true});const tmp=`${file}.${process.pid}.tmp`;await writeFile(tmp,JSON.stringify(value,null,2));await rename(tmp,file)}
export async function settings(){try{return{...defaults,...JSON.parse(await readFile(settingsFile,'utf8'))}}catch{return{...defaults}}}
export async function saveSettings(value){const clean={discoveryPort:Math.min(65535,Math.max(1,Number(value.discoveryPort)||3702)),onvifPort:Math.min(65535,Math.max(1024,Number(value.onvifPort)||8091)),rtspPort:Math.min(65535,Math.max(1024,Number(value.rtspPort)||8554)),autoDiscovery:value.autoDiscovery!==false,fragmentMs:Math.min(2000,Math.max(50,Number(value.fragmentMs)||100)),gop:Math.min(300,Math.max(1,Number(value.gop)||5)),buffering:Boolean(value.buffering)};await mkdir(dir,{recursive:true});const tmp=`${settingsFile}.${process.pid}.tmp`;await writeFile(tmp,JSON.stringify(clean,null,2));await rename(tmp,settingsFile);return clean}
