import {readFile,lstat,mkdir,unlink,open,realpath} from 'node:fs/promises';
import {join,isAbsolute,resolve,relative,sep,dirname,basename} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createCameraStore} from '../../applications/rtsp_to_onvif/src/lib/server/camera-store.js';
import {relayConfig} from '../../applications/rtsp_to_onvif/src/lib/server/relay-config.js';
import {createRtspConnectClient} from '../../applications/rtsp_to_onvif/src/lib/server/connect-client.js';
import {writePrivateFile} from '../../applications/rtsp_to_onvif/src/lib/server/private-file.js';
import {MIGRATION_MARKER} from './migration-state.mjs';
const inside=(parent,child)=>{const value=relative(parent,child);return !value||(!value.startsWith('..'+sep)&&value!=='..'&&!isAbsolute(value));};
async function privateSource(path,required=true){
 let stat;try{stat=await lstat(path);}catch(error){if(!required&&error.code==='ENOENT')return null;throw Error('A required migration source file could not be read.');}
 if(!stat.isFile()||stat.isSymbolicLink()||stat.size>32*1024*1024)throw Error('Migration accepts only regular private configuration files up to 32 MiB.');
 return readFile(path);
}
export async function migrateConfiguration({source,target,sourceStopped=false,guiPort=8090}){
 if(!sourceStopped)throw Error('Stop the source camera application and explicitly acknowledge this before migration.');
 if(!isAbsolute(source||'')||!isAbsolute(target||''))throw Error('Use absolute source and target directories.');
 source=resolve(source);target=resolve(target);
 if(!(await lstat(source)).isDirectory())throw Error('Choose the source private camera directory.');
 source=await realpath(source);target=join(await realpath(dirname(target)),basename(target));
 if(inside(source,target)||inside(target,source))throw Error('Source and target directories must be separate.');
 const files=new Map();
 for(const name of ['cameras.json','settings.json','connect.json','.connect-key']){const value=await privateSource(join(source,name),name==='cameras.json');if(value!==null)files.set(name,value);}
 if(files.has('connect.json')!==files.has('.connect-key'))throw Error('Restore both Connect state and its encryption key before migration.');
 const store=createCameraStore(source),cameras=await store.cameras(),settings=await store.settings();relayConfig(cameras,settings);
 for(const port of [settings.onvifPort,settings.rtspPort,guiPort])if(!Number.isInteger(port)||port<1024||port>65535)throw Error('Verify the management, ONVIF and RTSP ports before migration.');
 if(new Set([settings.onvifPort,settings.rtspPort,guiPort]).size!==3)throw Error('Management, ONVIF and RTSP ports must be different.');
 if(files.has('connect.json'))createRtspConnectClient({path:join(source,'connect.json')}).view();
 try{await mkdir(target,{mode:0o700});}catch{throw Error('Migration requires a new, empty target directory; existing targets are never replaced.');}
 await writePrivateFile(join(target,MIGRATION_MARKER),'Migration is incomplete. Do not start the addon.\n');
 // Any later error deliberately retains this marker and the original source.
 for(const [name,value] of files)await writePrivateFile(join(target,name),value);
 for(const [name,value] of files){const current=await privateSource(join(source,name));if(!value.equals(current))throw Error('The source changed during migration. Keep both applications stopped and retain the source backup.');}
 const migrated=createCameraStore(target);assertSame(await migrated.cameras(),cameras);assertSame(await migrated.settings(),settings);
 if(files.has('connect.json'))createRtspConnectClient({path:join(target,'connect.json')}).view();
 await unlink(join(target,MIGRATION_MARKER));
 if(process.platform!=='win32'){const directory=await open(target,'r');try{await directory.sync();}finally{await directory.close();}}
 return {complete:true,camera_count:cameras.length,files:[...files.keys()],source_retained:true};
}
function assertSame(left,right){if(JSON.stringify(left)!==JSON.stringify(right))throw Error('The migrated configuration did not match the source.');}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
 const args=process.argv.slice(2),source=args[args.indexOf('--source')+1],target=args[args.indexOf('--target')+1];
 try{if(!args.includes('--source')||!args.includes('--target'))throw Error('Specify --source and --target directories.');const guiPort=args.includes('--gui-port')?Number(args[args.indexOf('--gui-port')+1]):8090;console.log(JSON.stringify(await migrateConfiguration({source,target,guiPort,sourceStopped:args.includes('--acknowledge-source-stopped')})));}
 catch{console.error('Migration was not completed. Check stopped source services, private source files, a new target directory and non-conflicting ports. The source was not removed; do not start a target containing .migration-in-progress.');process.exitCode=1;}
}
