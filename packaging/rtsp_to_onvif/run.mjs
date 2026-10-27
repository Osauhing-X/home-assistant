import {readFile} from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {runtimeOptions} from './runtime-options.mjs';
import {assertMigrationComplete} from './migration-state.mjs';
try{
 const env={...process.env,...runtimeOptions(JSON.parse(await readFile('/data/options.json','utf8')))};
 await assertMigrationComplete(env.RTSP_ONVIF_DATA);
 // This standalone process does not impersonate an X Platform application.
 for(const name of ['X_PLATFORM','X_APPLICATION_ID','X_INSTALLATION_ID','X_APPLICATION_DATA_DIR','X_ENTITIES_HUB_HOST','X_ENTITIES_HUB_PORT'])delete env[name];
 delete env.RTSP_ONVIF_OFFLINE_TEST;
 const child=spawn(process.execPath,['build/index.js'],{cwd:'/app',env,stdio:'inherit'});
 for(const signal of ['SIGTERM','SIGINT'])process.on(signal,()=>child.kill(signal));
 child.once('error',()=>{console.error('The camera relay could not be started.');process.exitCode=1;});
 child.once('exit',(code,signal)=>{process.exitCode=code??(signal==='SIGTERM'?0:1);});
}catch{
 console.error('Addon startup refused: check private addon options and any incomplete data migration. Existing camera data has not been changed.');process.exitCode=1;
}
