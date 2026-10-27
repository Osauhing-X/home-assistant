import test from 'node:test';
import assert from 'node:assert/strict';
import {displayStreamUrl} from '../src/lib/stream-display.js';
test('camera list source labels do not disclose passwords or query tokens',()=>{
 assert.equal(displayStreamUrl('rtsp://synthetic:private@camera.local:554/live?token=private-query#private-fragment'),'rtsp://camera.local:554/live?…');
 assert.equal(displayStreamUrl('rtsps://camera.local/live'),'rtsps://camera.local/live');
 assert.equal(displayStreamUrl('invalid private credential'),'Configured RTSP source');
});
