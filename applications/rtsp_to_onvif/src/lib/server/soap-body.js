export async function readSoapBody(request,limit=65536){
 const reader=request.body?.getReader();if(!reader)return Buffer.alloc(0);const chunks=[];let size=0;
 // Cancelling an adapter-node request body destroys its incoming socket before
 // the 413 response can be written. Stop reading; the response closes it instead.
 try{while(true){const {value,done}=await reader.read();if(done)break;size+=value.byteLength;if(size>limit)throw Error('SOAP body limit exceeded');chunks.push(value);}return Buffer.concat(chunks);}finally{reader.releaseLock();}
}
