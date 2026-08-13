import { error, json } from '@sveltejs/kit';
import { enqueue, getConfig } from '$lib/server/store.js';

const ACTIONS = new Set(['start', 'stop', 'restart', 'update', 'reload-code', 'install', 'sync-integrations', 'update-integration', 'delete-integration', 'update-all-integrations', 'scan-repository']);

export async function POST({ request }) {
  const input = await request.json();
  if (!ACTIONS.has(input.action)) error(400, 'Unknown action.');
  if (!['sync-integrations', 'update-integration', 'delete-integration', 'update-all-integrations', 'scan-repository'].includes(input.action)) {
    const config = await getConfig();
    if (!config.apps.some((app) => app.id === input.appId)) error(404, 'Application not found.');
  }
  await enqueue({ type: input.action, appId: input.appId, integrationId: input.integrationId, repository: input.repository });
  return json({ ok: true });
}
