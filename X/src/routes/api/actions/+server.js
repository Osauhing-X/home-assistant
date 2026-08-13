import { error, json } from '@sveltejs/kit';
import { enqueue, getConfig } from '$lib/server/store.js';

const ACTIONS = new Set(['start', 'stop', 'restart', 'update', 'reload-code', 'install', 'delete-application', 'sync-integrations', 'update-integration', 'delete-integration', 'scan-repository']);

export async function POST({ request }) {
  const input = await request.json();
  if (!ACTIONS.has(input.action)) error(400, 'Unknown action.');
  if (!['sync-integrations', 'update-integration', 'delete-integration', 'scan-repository'].includes(input.action)) {
    const config = await getConfig();
    const app = config.apps.find((item) => item.id === input.appId);
    if (!app) error(404, 'Application not found.');
    if (['install', 'start', 'restart', 'reload-code', 'update'].includes(input.action)) {
      const missingEnvironment = (app.envSchema || []).filter((item) => item.required && !String(app.env?.[item.name] || '').trim()).map((item) => item.name);
      if (missingEnvironment.length) error(400, `Required environment variables are missing: ${missingEnvironment.join(', ')}.`);
    }
  }
  await enqueue({ type: input.action, appId: input.appId, integrationId: input.integrationId, repository: input.repository, manual: ['start', 'restart'].includes(input.action) });
  return json({ ok: true });
}
