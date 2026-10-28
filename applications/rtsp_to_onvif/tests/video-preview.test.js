import test from 'node:test';
import assert from 'node:assert/strict';
import {stopVideo,playVideo,releaseVideo} from '../src/lib/video-preview.js';
test('ending or removing a preview detaches its source rather than leaving a paused streaming request',async()=>{
 const calls=[],video={src:'old',style:{},pause(){calls.push('pause');},removeAttribute(key){calls.push(key);this.src='';},load(){calls.push('load');},play(){calls.push('play');return Promise.resolve();}};
 playVideo(video,'/api/stream?id=synthetic');assert.equal(video.src,'/api/stream?id=synthetic');
 stopVideo(video);assert.equal(video.src,'');assert.deepEqual(calls.slice(-3),['pause','src','load']);
 video.src='again';releaseVideo(video).destroy();assert.equal(video.src,'');
 video.play=()=>Promise.reject(Error('Decoder unavailable'));playVideo(video,'retry');await new Promise(resolve=>setImmediate(resolve));assert.equal(video.src,'');
 assert.doesNotThrow(()=>stopVideo(null));
});
