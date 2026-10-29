import assert from 'node:assert/strict';import fs from 'node:fs';
import {currentHostPlatform,assertPackageHost} from '/app/runtime/host_platform.js';
let ready=false;for(let i=0;i<90;i++){try{const r=await fetch('http://127.0.0.1:3000/health');const body=await r.json();if(r.ok&&body.ok===true&&body.service==='workspace-core'){ready=true;break;}}catch{}await new Promise(resolve=>setTimeout(resolve,500));}assert.ok(ready,'Shared Core did not become healthy');
assert.equal(currentHostPlatform(),'home-assistant');assert.doesNotThrow(()=>assertPackageHost({platforms:['home-assistant']}));assert.throws(()=>assertPackageHost({platforms:['standalone']}));
const pidEnv=fs.readFileSync('/proc/1/environ','utf8');assert.ok(!pidEnv.split('\0').some(value=>/^(SUPERVISOR_TOKEN|HASSIO_TOKEN)=/.test(value)),'Supervisor control credentials reached Core');assert.match(fs.readFileSync('/proc/1/status','utf8'),/Uid:\s+1000\s/);
assert.equal((await fetch('http://127.0.0.1:3000/login')).status,200);
const marker='/data/.workspace-addon-acceptance';if(process.argv[2]==='after-restart')assert.equal(fs.readFileSync(marker,'utf8'),'synthetic-persistence');else fs.writeFileSync(marker,'synthetic-persistence',{mode:0o600});console.log('Shared Core healthy; host restriction, credential isolation and persistence accepted.');
