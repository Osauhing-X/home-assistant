import { readFile } from 'node:fs/promises';
import { json } from '@sveltejs/kit';
import { AUDIT_FILE } from '$lib/server/store.js';
export async function GET({ url }) { const scope=url.searchParams.get('scope')||'',query=(url.searchParams.get('q')||'').toLowerCase();try{const events=(await readFile(AUDIT_FILE,'utf8')).trim().split('\n').filter(Boolean).map(line=>JSON.parse(line)).filter(item=>(!scope||item.scope===scope)&&(!query||JSON.stringify(item).toLowerCase().includes(query))).slice(-500).reverse();return json({events})}catch{return json({events:[]})} }
