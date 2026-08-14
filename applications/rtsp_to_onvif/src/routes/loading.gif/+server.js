import { readFile } from 'node:fs/promises';
import path from 'node:path';
export async function GET(){return new Response(await readFile(path.resolve('loading.gif')),{headers:{'content-type':'image/gif','cache-control':'public, max-age=86400'}})}
