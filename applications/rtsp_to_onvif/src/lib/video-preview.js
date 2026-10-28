// Pausing alone keeps the streaming request and its FFmpeg process alive.
const generations=new WeakMap();
export function stopVideo(video){
 if(!video)return;
 generations.set(video,(generations.get(video)||0)+1);
 video.pause();video.removeAttribute('src');video.load();video.style.background='#080d13';
}
export function releaseVideo(video){return {destroy(){stopVideo(video);}};}
export function playVideo(video,src){
 if(!video)return;
 stopVideo(video);video.src=src;
 const generation=generations.get(video);
 try{const result=video.play();result?.catch(()=>{if(generations.get(video)===generation)stopVideo(video);});}
 catch{if(generations.get(video)===generation)stopVideo(video);}
}
