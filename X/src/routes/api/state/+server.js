import { json } from '@sveltejs/kit';
import { BUILT_INS, getConfig, getStatus, publicConfig } from '$lib/server/store.js';

export async function GET() {
  return json({ config: publicConfig(await getConfig()), status: await getStatus(), catalog: BUILT_INS });
}

