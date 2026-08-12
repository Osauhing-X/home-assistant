import { json } from '@sveltejs/kit';
import { audit, getConfig, saveConfig } from '$lib/server/store.js';

export async function PUT({ request }) {
  const input = await request.json();
  const config = await getConfig();
  if (typeof input.githubOAuthClientId === 'string') config.githubOAuthClientId = input.githubOAuthClientId.trim();
  if (input.account?.token) {
    const id = input.account.id || `pat-${Date.now()}`;
    const account = { id, login: input.account.login || 'Personal access token', type: 'pat', token: input.account.token.trim() };
    config.githubAccounts = [...(config.githubAccounts || []).filter((item) => item.id !== id), account];
  }
  if (input.removeAccountId) config.githubAccounts = (config.githubAccounts || []).filter((item) => item.id !== input.removeAccountId);
  if (typeof input.publicHost === 'string') {
    const host = input.publicHost.trim();
    if (host && !/^[A-Za-z0-9.-]+$/.test(host)) return json({ error: 'LAN host must be an IP address or host name.' }, { status: 400 });
    config.publicHost = host;
  }
  if (input.installer && typeof input.installer === 'object') config.installer = { ...config.installer, ...input.installer };
  if (input.notifications && typeof input.notifications === 'object') config.notifications = { ...config.notifications, ...input.notifications };
  if (input.updateChecks?.interval) config.updateChecks = { ...config.updateChecks, interval: Number(input.updateChecks.interval) };
  await saveConfig(config);
  await audit('portal', 'settings', 'changed', Object.keys(input).join(', '));
  return json({ ok: true });
}
