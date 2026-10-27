import {spawn} from 'node:child_process';
import {cameras} from '$lib/server/store.js';
import {createSnapshotHandler} from '$lib/server/snapshot.js';
export const GET=createSnapshotHandler({cameras,spawn});