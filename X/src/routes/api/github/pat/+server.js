import { error, json } from '@sveltejs/kit';
import { audit, getConfig, saveConfig } from '$lib/server/store.js';

export async function POST({ request, fetch }) {
  const input = await request.json();
  const token = String(input.token || '').trim();
  if (!token) error(400, 'Enter a GitHub personal access token.');

  const response = await fetch('https://api.github.com/user', {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    }
  });
  if (!response.ok) {
    const result = await response.json().catch(() => ({}));
    error(response.status, result.message || 'GitHub rejected the personal access token.');
  }

  const profile = await response.json();
  const account = {
    id: `github-${profile.id}`,
    login: profile.login,
    avatarUrl: profile.avatar_url,
    type: 'pat',
    token
  };
  const config = await getConfig();
  config.githubAccounts = [...(config.githubAccounts || []).filter((item) => item.id !== account.id), account];
  await saveConfig(config);
  await audit('portal', profile.login, 'github_pat_connected');
  return json({ connected: true, account: { ...account, token: undefined, tokenConfigured: true } });
}
