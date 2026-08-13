import { mkdir,readFile,rename,writeFile } from 'node:fs/promises';
import path from 'node:path';
const dir=process.env.RTSP_ONVIF_DATA||path.join(process.env.DATA_DIR||path.resolve('.data'),'application-data','rtsp-to-onvif');
const file=path.join(dir,'cameras.json');
export async function cameras(){try{return JSON.parse(await readFile(file,'utf8'))}catch{return[]}}
export async function save(value){await mkdir(dir,{recursive:true});const tmp=`${file}.${process.pid}.tmp`;await writeFile(tmp,JSON.stringify(value,null,2));await rename(tmp,file)}
