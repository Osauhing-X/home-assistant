import { json } from '@sveltejs/kit';
import { settings, saveSettings } from '$lib/server/store.js';
import { restartDiscovery } from '$lib/server/discovery.js';
export async function GET(){return json(await settings())}
export async function PUT({request}){const value=await saveSettings(await request.json());await restartDiscovery();return json(value)}
