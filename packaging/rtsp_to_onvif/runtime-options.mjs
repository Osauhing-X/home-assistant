export function runtimeOptions(options){
 if(!options||typeof options!=='object'||Array.isArray(options))throw Error('The addon options must be an object.');
 if(typeof options.password!=='string'||options.password.length<12||options.password.length>1024)throw Error('Set a management password containing 12 to 1024 characters.');
 if(!Number.isInteger(options.port)||options.port<1024||options.port>65535)throw Error('Set a GUI port between 1024 and 65535.');
 let origin;try{origin=new URL(options.public_origin);}catch{throw Error('Set the exact public origin, for example http://192.168.1.20:8090.');}
 if(!['http:','https:'].includes(origin.protocol)||origin.username||origin.password||origin.pathname!=='/'||origin.search||origin.hash||['0.0.0.0','[::]'].includes(origin.hostname))throw Error('Set an HTTP or HTTPS origin without credentials, a path, query or fragment.');
 return {NODE_ENV:'production',HOST:'0.0.0.0',PORT:String(options.port),ORIGIN:origin.origin,PASSWORD:options.password,
  DATA_DIR:'/data',RTSP_ONVIF_DATA:'/data/application-data/rtsp-to-onvif',RTSP_CONNECT_ENABLED:'true'};
}
