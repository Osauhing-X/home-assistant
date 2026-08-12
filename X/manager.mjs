import { fileURLToPath } from 'node:url';
import { getConfig } from './src/lib/server/store.js';
import { boot, consumeCommands, scheduledUpdateCheck } from './tasks/orchestrator.js';
import { syncIntegrations } from './tasks/integrations.js';
import { initializeRuntime, stopChildren } from './tasks/runtime.js';

await initializeRuntime();

process.on('SIGTERM', () => { stopChildren(); process.exit(0); });
process.on('SIGINT', () => { stopChildren(); process.exit(0); });

await boot();
setInterval(consumeCommands, 1000);
setInterval(scheduledUpdateCheck, 60000);
setInterval(syncIntegrations, Math.max(60, (await getConfig()).installer.interval || 3600) * 1000);

console.log(`[X Platform] Manager ready (${fileURLToPath(import.meta.url)})`);
